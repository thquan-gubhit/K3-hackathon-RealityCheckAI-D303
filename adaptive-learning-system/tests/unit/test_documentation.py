"""Documentation integrity and Phase 6 traceability checks."""

from __future__ import annotations

from pathlib import Path
import re


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def test_required_documentation_exists_and_local_links_resolve() -> None:
    markdown_files = [PROJECT_ROOT / "README.md", *sorted((PROJECT_ROOT / "docs").glob("*.md"))]
    assert len(markdown_files) >= 17

    broken: list[str] = []
    for document in markdown_files:
        content = document.read_text(encoding="utf-8")
        assert content.count("```") % 2 == 0, document
        for raw_target in MARKDOWN_LINK.findall(content):
            target = raw_target.strip().strip("<>")
            if (
                not target
                or target.startswith(("#", "http://", "https://", "mailto:"))
            ):
                continue
            relative_path = target.split("#", 1)[0]
            resolved = (document.parent / relative_path).resolve()
            if not resolved.exists():
                broken.append(f"{document.name}: {target}")

    assert broken == []


def test_phase_status_documents_are_synchronized() -> None:
    progress = (PROJECT_ROOT / "docs" / "PROGRESS.md").read_text(
        encoding="utf-8"
    )
    todo = (PROJECT_ROOT / "docs" / "TODO.md").read_text(encoding="utf-8")

    for phase in range(1, 7):
        assert f"{phase} —" in progress
        assert f"Phase {phase}" in todo
