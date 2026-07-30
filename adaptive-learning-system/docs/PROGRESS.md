# Project Progress

## Current phase

**Phase 1 — Project foundation: completed and runtime-verified.**

Python 3.11.9 was located at its per-user installation path, used to create the
project-local `.venv`, and used for the final verification. Product Phases 2–6
remain outside the completed Phase 1 scope.

## Phase status

| Phase | Status | Notes |
| --- | --- | --- |
| 1 — Project foundation | **Completed and verified** | Structure, config, SQLite bootstrap, health API, Streamlit home, tests, docs |
| 2 — Document processing | Pending | No PDF upload/parser or Knowledge Map implementation claimed |
| 3 — Question and evaluation | Pending | No question generation or answer evaluation implementation claimed |
| 4 — Adaptive learning | Pending | No session routing, mastery update, or dashboard implementation claimed |
| 5 — Tutor Agent | Pending | No agent runner, tools, trigger execution, or trace persistence implemented |
| 6 — Hardening | Pending | Full suite, demo seed, error/logging polish and final docs |

## Completed

- Created the modular project structure and package boundaries.
- Added Python 3.11 dependency and pytest configuration.
- Added typed `.env` configuration, secret-safe startup validation, and `.env.example`.
- Added SQLAlchemy engine/session and SQLite initialization script.
- Added FastAPI application with `GET /health`.
- Added Streamlit home and a transport-only backend health client.
- Added 15 Phase 1 tests covering configuration/security, database bootstrap,
  health API, structured logging, frontend transport, and Streamlit Home.
- Ran all 15 tests successfully on Python 3.11.9.
- Measured 89% total coverage across `app` and `frontend`.
- Initialized the default SQLite file and verified its schema marker/query.
- Smoke-tested Uvicorn `/health` and Streamlit HTTP health/startup.
- Executed Streamlit Home against the live backend; it rendered
  `Backend is online.` without an exception.
- Created all mandatory design, runbook, progress, decision, TODO, and development-log documents.

## In progress

None. Phase 2 has not started.

## Blocked

None for Phase 1.

## Verification evidence

```text
python scripts/init_db.py
→ Database initialized successfully; data/app.db = 4096 bytes

pytest -v --cov=app --cov=frontend --cov-report=term-missing
→ 15 passed, 1 upstream deprecation warning, 89% total coverage

GET http://127.0.0.1:8000/health
→ HTTP 200 with status/app_name/environment/database

Streamlit server + AppTest
→ HTTP 200, /_stcore/health = ok, Home title rendered,
  Backend is online., no Streamlit exception
```

## Next actions

1. Start Phase 2 with PDF validation and page-level extraction.
2. Add `Document` and `DocumentPage` persistence.
3. Implement Pydantic Knowledge Unit extraction and deterministic split/merge rules.
4. Update this file, `TODO.md`, `DECISIONS.md` if architecture changes, and `VIBE_CODING_LOG.md` after Phase 2.
