"""Offline tests for safe Pydantic parsing and bounded LLM retries."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import logging
from typing import Any

import pytest
from pydantic import BaseModel, Field

from app.config import Settings
from app.llm.adapter import InvalidLLMOutputError, LLMClient
from app.llm.client import LLMTimeoutError
from app.llm.structured_outputs import (
    StructuredOutputError,
    parse_structured_output,
)


class ExampleOutput(BaseModel):
    title: str = Field(min_length=1)
    pages: list[int] = Field(min_length=1)


class ScriptedTransport:
    def __init__(self, outcomes: Sequence[object]) -> None:
        self.outcomes = list(outcomes)
        self.calls: list[dict[str, object]] = []

    def complete(
        self,
        *,
        messages: Sequence[Mapping[str, str]],
        temperature: float,
        response_format: Mapping[str, Any],
    ) -> str:
        self.calls.append(
            {
                "messages": messages,
                "temperature": temperature,
                "response_format": response_format,
            }
        )
        outcome = self.outcomes[len(self.calls) - 1]
        if isinstance(outcome, BaseException):
            raise outcome
        assert isinstance(outcome, str)
        return outcome


def _settings(*, retries: int = 2, api_key: str = "secret-unit-test-key") -> Settings:
    return Settings(
        _env_file=None,
        llm_api_key=api_key,
        llm_base_url="https://llm.invalid/v1",
        llm_model="offline-test-model",
        llm_max_retries=retries,
        llm_timeout_seconds=0.5,
    )


def _messages() -> list[dict[str, str]]:
    return [{"role": "user", "content": "Return the fixture object."}]


def test_parse_valid_structured_json() -> None:
    result = parse_structured_output(
        '{"title":"Generalization","pages":[2,3]}',
        ExampleOutput,
    )

    assert result.title == "Generalization"
    assert result.pages == [2, 3]


def test_parse_json_code_fence() -> None:
    result = parse_structured_output(
        '```json\n{"title":"Overfitting","pages":[4]}\n```',
        ExampleOutput,
    )

    assert result == ExampleOutput(title="Overfitting", pages=[4])


def test_malformed_json_is_rejected_without_raw_output() -> None:
    raw = '{"title":"private source fragment"'

    with pytest.raises(StructuredOutputError) as captured:
        parse_structured_output(raw, ExampleOutput)

    assert captured.value.code == "MALFORMED_JSON"
    assert "private source fragment" not in str(captured.value)


def test_schema_mismatch_reports_only_field_locations() -> None:
    with pytest.raises(StructuredOutputError) as captured:
        parse_structured_output(
            '{"title":"Generalization","pages":[]}',
            ExampleOutput,
        )

    assert captured.value.code == "SCHEMA_VALIDATION_FAILED"
    assert captured.value.field_locations == ("pages",)


def test_adapter_retries_invalid_json_then_returns_valid_model() -> None:
    transport = ScriptedTransport(
        [
            "not-json",
            '{"title":"Generalization","pages":[1]}',
        ]
    )
    client = LLMClient(_settings(retries=2), transport=transport)

    result = client.generate_structured(_messages(), ExampleOutput)

    assert result.pages == [1]
    assert len(transport.calls) == 2
    second_messages = transport.calls[1]["messages"]
    assert isinstance(second_messages, list)
    assert "MALFORMED_JSON" in second_messages[-1]["content"]


def test_adapter_exhausts_exact_retry_budget_and_never_logs_secret(
    caplog: pytest.LogCaptureFixture,
) -> None:
    secret = "do-not-log-this-api-key"
    transport = ScriptedTransport([secret, secret, secret])
    client = LLMClient(
        _settings(retries=2, api_key=secret),
        transport=transport,
    )

    with caplog.at_level(logging.WARNING):
        with pytest.raises(InvalidLLMOutputError) as captured:
            client.generate_structured(_messages(), ExampleOutput)

    assert captured.value.attempts == 3
    assert len(transport.calls) == 3
    assert secret not in caplog.text
    assert secret not in str(captured.value)


def test_adapter_timeout_retries_are_bounded() -> None:
    transport = ScriptedTransport([TimeoutError(), TimeoutError()])
    client = LLMClient(_settings(retries=1), transport=transport)

    with pytest.raises(LLMTimeoutError):
        client.generate_structured(_messages(), ExampleOutput)

    assert len(transport.calls) == 2


def test_adapter_uses_configured_temperature_and_json_mode() -> None:
    transport = ScriptedTransport(
        ['{"title":"Generalization","pages":[1]}']
    )
    client = LLMClient(_settings(retries=0), transport=transport)

    client.generate_structured(_messages(), ExampleOutput, temperature=0.4)

    assert transport.calls[0]["temperature"] == 0.4
    assert transport.calls[0]["response_format"] == {"type": "json_object"}
