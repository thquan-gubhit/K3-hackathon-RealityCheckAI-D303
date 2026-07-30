"""Low-level, OpenAI-compatible chat-completion transport."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Literal, Protocol, TypedDict

from openai import APITimeoutError, OpenAI, OpenAIError

from app.config import Settings


class ChatMessage(TypedDict):
    """Provider-neutral message accepted by the structured LLM adapter."""

    role: Literal["system", "user", "assistant"]
    content: str


class LLMError(RuntimeError):
    """Base class for safe, application-facing LLM failures."""


class UnsupportedLLMProviderError(LLMError):
    """Raised when a provider cannot use the OpenAI-compatible transport."""


class LLMProviderError(LLMError):
    """Raised for a provider/network error without exposing provider payloads."""


class LLMTimeoutError(LLMProviderError):
    """Raised when the configured provider request timeout is exceeded."""


class CompletionTransport(Protocol):
    """Injectable transport used by :class:`app.llm.adapter.LLMClient`."""

    def complete(
        self,
        *,
        messages: Sequence[Mapping[str, str]],
        temperature: float,
        response_format: Mapping[str, Any],
    ) -> str:
        """Return the assistant message content for one bounded request."""


def _extract_text_content(content: object) -> str:
    if isinstance(content, str) and content.strip():
        return content

    # A few compatible providers return a list of content parts rather than a
    # single string. Accept only explicit text parts, never stringify an
    # arbitrary response object (which could expose headers or metadata).
    if isinstance(content, list):
        text_parts: list[str] = []
        for part in content:
            if isinstance(part, Mapping):
                text = part.get("text")
            else:
                text = getattr(part, "text", None)
            if isinstance(text, str):
                text_parts.append(text)
        joined = "".join(text_parts)
        if joined.strip():
            return joined

    raise LLMProviderError("The LLM provider returned no text content.")


class OpenAICompatibleClient:
    """Synchronous OpenAI-compatible transport with a per-request timeout.

    SDK retries are disabled because the higher-level structured adapter owns
    the single, auditable retry budget.
    """

    def __init__(self, settings: Settings) -> None:
        settings.validate_runtime_requirements()
        provider = settings.llm_provider.strip().casefold()
        if provider not in {"openai_compatible", "openai", "openrouter"}:
            raise UnsupportedLLMProviderError(
                "LLM_PROVIDER must use an OpenAI-compatible API."
            )

        self._model = settings.llm_model
        self._timeout_seconds = settings.llm_timeout_seconds
        self._client = OpenAI(
            api_key=settings.llm_api_key.get_secret_value(),
            base_url=settings.llm_base_url,
            timeout=settings.llm_timeout_seconds,
            max_retries=0,
        )

    def complete(
        self,
        *,
        messages: Sequence[Mapping[str, str]],
        temperature: float,
        response_format: Mapping[str, Any],
    ) -> str:
        normalized_messages = [
            {"role": message["role"], "content": message["content"]}
            for message in messages
        ]
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=normalized_messages,  # type: ignore[arg-type]
                temperature=temperature,
                response_format=dict(response_format),  # type: ignore[arg-type]
                timeout=self._timeout_seconds,
            )
        except APITimeoutError:
            raise LLMTimeoutError(
                "The LLM provider exceeded the configured timeout."
            ) from None
        except OpenAIError:
            raise LLMProviderError("The LLM provider request failed.") from None

        if not response.choices:
            raise LLMProviderError("The LLM provider returned no completion.")
        return _extract_text_content(response.choices[0].message.content)


__all__ = [
    "ChatMessage",
    "CompletionTransport",
    "LLMError",
    "LLMProviderError",
    "LLMTimeoutError",
    "OpenAICompatibleClient",
    "UnsupportedLLMProviderError",
]
