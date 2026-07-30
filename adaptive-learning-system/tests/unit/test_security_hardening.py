"""Static guards for local secrets, uploads, and source-text logging."""

from __future__ import annotations

import ast
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_sensitive_local_artifacts_are_ignored() -> None:
    ignore = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")

    assert ".env" in ignore
    assert "data/app.db" in ignore
    assert "data/uploads/*" in ignore
    assert ".streamlit/secrets.toml" in ignore


def test_application_logger_calls_do_not_include_full_source_fields() -> None:
    forbidden = {
        "raw_text",
        "cleaned_text",
        "source_context",
        "reference_answer",
        "llm_api_key",
    }
    violations: list[str] = []

    for path in sorted((PROJECT_ROOT / "app").rglob("*.py")):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            function = node.func
            if not (
                isinstance(function, ast.Attribute)
                and isinstance(function.value, ast.Name)
                and function.value.id == "logger"
            ):
                continue
            call_source = ast.get_source_segment(source, node) or ""
            found = {field for field in forbidden if field in call_source}
            if found:
                violations.append(
                    f"{path.relative_to(PROJECT_ROOT)}: {sorted(found)}"
                )

    assert violations == []
