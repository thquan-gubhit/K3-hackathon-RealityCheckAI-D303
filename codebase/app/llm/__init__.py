"""Public LLM boundary for provider-neutral structured generation."""

from app.llm.adapter import InvalidLLMOutputError, LLMClient
from app.llm.client import (
    ChatMessage,
    CompletionTransport,
    LLMError,
    LLMProviderError,
    LLMTimeoutError,
    OpenAICompatibleClient,
    UnsupportedLLMProviderError,
)
from app.llm.structured_outputs import StructuredOutputError


__all__ = [
    "ChatMessage",
    "CompletionTransport",
    "InvalidLLMOutputError",
    "LLMClient",
    "LLMError",
    "LLMProviderError",
    "LLMTimeoutError",
    "OpenAICompatibleClient",
    "StructuredOutputError",
    "UnsupportedLLMProviderError",
]
