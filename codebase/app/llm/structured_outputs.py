"""Safe parsing helpers for schema-constrained LLM JSON responses."""

from __future__ import annotations

from collections.abc import Mapping
import json
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError


ModelT = TypeVar("ModelT", bound=BaseModel)


class StructuredOutputError(ValueError):
    """Raised when provider output is not valid for the requested schema.

    The exception deliberately stores only error codes and field locations. It
    never embeds the raw provider output, which may contain document content.
    """

    def __init__(
        self,
        code: str,
        message: str,
        *,
        field_locations: tuple[str, ...] = (),
    ) -> None:
        self.code = code
        self.field_locations = field_locations
        super().__init__(message)


def _strip_json_fence(raw_text: str) -> str:
    text = raw_text.strip()
    if not text.startswith("```"):
        return text

    lines = text.splitlines()
    if len(lines) < 3 or lines[-1].strip() != "```":
        raise StructuredOutputError(
            "MALFORMED_JSON",
            "The model returned an incomplete JSON code fence.",
        )
    opening = lines[0].strip().casefold()
    if opening not in {"```", "```json"}:
        raise StructuredOutputError(
            "MALFORMED_JSON",
            "The model returned an unsupported structured-output code fence.",
        )
    return "\n".join(lines[1:-1]).strip()


def _validation_locations(error: ValidationError) -> tuple[str, ...]:
    locations: list[str] = []
    for item in error.errors(include_input=False, include_url=False):
        location = ".".join(str(part) for part in item.get("loc", ()))
        locations.append(location or "<root>")
    return tuple(locations)


def parse_structured_output(
    raw_output: str | bytes | bytearray | Mapping[str, Any],
    response_model: type[ModelT],
) -> ModelT:
    """Parse one complete JSON value and validate it with ``response_model``."""

    if isinstance(raw_output, Mapping):
        payload: Any = dict(raw_output)
    else:
        if isinstance(raw_output, (bytes, bytearray)):
            try:
                raw_text = bytes(raw_output).decode("utf-8")
            except UnicodeDecodeError:
                raise StructuredOutputError(
                    "MALFORMED_JSON",
                    "The model response is not valid UTF-8 JSON.",
                ) from None
        elif isinstance(raw_output, str):
            raw_text = raw_output
        else:
            raise StructuredOutputError(
                "MALFORMED_JSON",
                "The model response is not a JSON string or object.",
            )

        json_text = _strip_json_fence(raw_text)
        if not json_text:
            raise StructuredOutputError(
                "EMPTY_OUTPUT",
                "The model returned an empty structured response.",
            )
        try:
            payload = json.loads(json_text)
        except json.JSONDecodeError:
            raise StructuredOutputError(
                "MALFORMED_JSON",
                "The model response is not valid JSON.",
            ) from None

    try:
        return response_model.model_validate(payload)
    except ValidationError as error:
        raise StructuredOutputError(
            "SCHEMA_VALIDATION_FAILED",
            f"The model JSON does not match {response_model.__name__}.",
            field_locations=_validation_locations(error),
        ) from None


def compact_json_schema(response_model: type[BaseModel]) -> str:
    """Return a compact schema suitable for embedding in a bounded prompt."""

    return json.dumps(
        response_model.model_json_schema(),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


__all__ = [
    "StructuredOutputError",
    "compact_json_schema",
    "parse_structured_output",
]
