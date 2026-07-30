"""Schema-validating LLM adapter with one bounded retry budget."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import logging
from time import monotonic
from typing import TypeVar

from pydantic import BaseModel

from app.config import Settings
from app.llm.client import (
    CompletionTransport,
    LLMError,
    LLMProviderError,
    LLMTimeoutError,
    OpenAICompatibleClient,
)
from app.llm.structured_outputs import (
    StructuredOutputError,
    compact_json_schema,
    parse_structured_output,
)


logger = logging.getLogger(__name__)
ModelT = TypeVar("ModelT", bound=BaseModel)


class InvalidLLMOutputError(LLMError):
    """Raised after all schema-validation attempts have failed."""

    def __init__(
        self,
        *,
        schema_name: str,
        attempts: int,
        validation_code: str,
        field_locations: tuple[str, ...] = (),
    ) -> None:
        self.schema_name = schema_name
        self.attempts = attempts
        self.validation_code = validation_code
        self.field_locations = field_locations
        super().__init__(
            f"LLM output did not match {schema_name} after {attempts} "
            f"attempt(s): {validation_code}."
        )


def _normalize_messages(
    messages: Sequence[Mapping[str, str]],
) -> list[dict[str, str]]:
    if not messages:
        raise ValueError("messages must not be empty")

    normalized: list[dict[str, str]] = []
    supported_roles = {"system", "user", "assistant"}
    for message in messages:
        role = message.get("role", "").strip().casefold()
        content = message.get("content", "")
        if role not in supported_roles:
            raise ValueError(f"unsupported LLM message role: {role or '<empty>'}")
        if not isinstance(content, str) or not content.strip():
            raise ValueError("LLM message content must be a non-empty string")
        normalized.append({"role": role, "content": content})
    return normalized


class LLMClient:
    """OpenAI-compatible structured-output adapter.

    ``llm_max_retries`` means retries after the first request, so the exact
    upper bound is ``llm_max_retries + 1`` provider calls.
    """

    def __init__(
        self,
        settings: Settings,
        transport: CompletionTransport | None = None,
    ) -> None:
        settings.validate_runtime_requirements()
        self._settings = settings
        self._transport = transport or OpenAICompatibleClient(settings)

    def generate_structured(
        self,
        messages: Sequence[Mapping[str, str]],
        response_model: type[ModelT],
        temperature: float | None = None,
    ) -> ModelT:
        """Return a Pydantic-valid response or a safe bounded failure."""

        normalized_messages = _normalize_messages(messages)
        selected_temperature = (
            self._settings.llm_temperature
            if temperature is None
            else temperature
        )
        if not 0.0 <= selected_temperature <= 2.0:
            raise ValueError("temperature must be between 0 and 2")

        schema_instruction = {
            "role": "system",
            "content": (
                "Return exactly one JSON object and no prose. It must match "
                f"this JSON Schema: {compact_json_schema(response_model)}"
            ),
        }
        base_messages = [schema_instruction, *normalized_messages]
        total_attempts = self._settings.llm_max_retries + 1
        last_structured_error: StructuredOutputError | None = None

        for attempt in range(1, total_attempts + 1):
            attempt_messages = list(base_messages)
            if last_structured_error is not None:
                fields = ", ".join(last_structured_error.field_locations[:10])
                correction = (
                    "The previous response was invalid "
                    f"({last_structured_error.code}). Correct the JSON and "
                    "return the complete object only."
                )
                if fields:
                    correction += f" Check these fields: {fields}."
                attempt_messages.append({"role": "user", "content": correction})

            started = monotonic()
            try:
                raw_output = self._transport.complete(
                    messages=attempt_messages,
                    temperature=selected_temperature,
                    response_format={"type": "json_object"},
                )
                parsed = parse_structured_output(raw_output, response_model)
            except StructuredOutputError as error:
                last_structured_error = error
                logger.warning(
                    "llm_structured_retry model=%s schema=%s attempt=%d "
                    "failure=%s",
                    self._settings.llm_model,
                    response_model.__name__,
                    attempt,
                    error.code,
                )
                if attempt == total_attempts:
                    raise InvalidLLMOutputError(
                        schema_name=response_model.__name__,
                        attempts=attempt,
                        validation_code=error.code,
                        field_locations=error.field_locations,
                    ) from None
                continue
            except (LLMTimeoutError, TimeoutError):
                logger.warning(
                    "llm_structured_retry model=%s schema=%s attempt=%d "
                    "failure=timeout",
                    self._settings.llm_model,
                    response_model.__name__,
                    attempt,
                )
                if attempt == total_attempts:
                    raise LLMTimeoutError(
                        "The LLM provider exceeded the configured timeout "
                        f"after {attempt} attempt(s)."
                    ) from None
                continue
            except LLMProviderError:
                logger.warning(
                    "llm_structured_retry model=%s schema=%s attempt=%d "
                    "failure=provider_error",
                    self._settings.llm_model,
                    response_model.__name__,
                    attempt,
                )
                if attempt == total_attempts:
                    raise LLMProviderError(
                        "The LLM provider request failed after "
                        f"{attempt} attempt(s)."
                    ) from None
                continue

            latency_ms = round((monotonic() - started) * 1_000)
            logger.info(
                "llm_structured_success model=%s schema=%s attempt=%d "
                "latency_ms=%d",
                self._settings.llm_model,
                response_model.__name__,
                attempt,
                latency_ms,
            )
            return parsed

        # The loop always returns or raises. This guard protects future edits.
        raise RuntimeError("unreachable structured LLM state")


__all__ = ["InvalidLLMOutputError", "LLMClient"]
