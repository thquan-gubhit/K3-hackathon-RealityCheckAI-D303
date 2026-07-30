# Vibe Coding Log

Do not record API keys, secrets, authorization headers, full private documents, or chain-of-thought in this log.

## 2026-07-30 12:26 +07:00 — Phase 1 project foundation

### Goal

Create a local Python 3.11 foundation with typed configuration, SQLite/SQLAlchemy bootstrap, a FastAPI health endpoint, a Streamlit home page, baseline tests, and the complete initial Markdown design set. Do not implement PDF processing or the Tutor Agent.

### Files created

- Application foundation under `app/`, including configuration, database, and FastAPI entry point.
- Streamlit home and backend health client under `frontend/`.
- Database/backend/frontend launch scripts under `scripts/`.
- Phase 1 unit and integration tests under `tests/`.
- `.env.example`, `.gitignore`, `requirements.txt`, `pyproject.toml`, and `README.md`.
- `docs/00_OVERVIEW.md` through `docs/12_RUNBOOK.md`.
- `docs/DECISIONS.md`, `docs/PROGRESS.md`, `docs/TODO.md`, and this log.

### Files modified

- None; this was a greenfield Phase 1 project directory.

### Technical decisions

- Use a local modular monolith: FastAPI + Streamlit + SQLite/SQLAlchemy.
- Load typed settings with `pydantic-settings` and validate required LLM values at startup.
- Keep `/health` provider-independent and return only non-sensitive configuration readiness.
- Keep workflows as the normal orchestration mechanism and reserve a bounded agent for Phase 5 exceptions.
- Treat all later-phase schemas, rules, workflows, ER entities, and endpoints in docs as design contracts, not implementation claims.

### Commands executed

Runtime discovery attempted:

```text
python --version
py -0p
py -3.11 --version
```

These commands confirmed that Python was not discoverable through `PATH` or the
Windows launcher at that point. A later check found a per-user Python 3.11.9
installation and enabled full verification; see the next entry.

### Tests executed

None during the initial implementation pass because no runtime was discoverable
through `PATH` or the Windows launcher.

### Test results

Not executed during this initial pass. Final results are recorded below.

### Known issues

- Runtime verification was pending at the end of this initial pass.
- PDF ingestion, Knowledge Unit processing, questions/evaluation, adaptive learning, and Tutor Agent execution are intentionally not implemented in Phase 1.

### Next step

Locate or install Python 3.11, verify Phase 1, then begin Phase 2 document processing.

## 2026-07-30 14:06 +07:00 — Phase 1 audit, fixes, and runtime verification

### Goal

Audit the foundation against the master prompt, fix concrete compliance/runtime
issues, and verify database, backend, frontend, and tests on Python 3.11.

### Files created

- `app/logging_config.py` for valid JSON log records.
- `tests/integration/test_database.py`.
- `tests/integration/test_frontend_home.py`.
- `tests/unit/test_logging.py`.

### Files modified

- Configuration, database, FastAPI logging, frontend client/Home, scripts, and
  Phase 1 tests.
- Evaluation, API, test-plan, runbook, progress, TODO, and development-log docs.

### Technical decisions

- Keep provider base URLs exclusively in environment configuration, not source.
- Require `BACKEND_API_URL` from environment configuration instead of guessing a
  frontend fallback URL.
- Validate `LLM_API_KEY`, `LLM_BASE_URL`, and `LLM_MODEL` at startup.
- Anchor default SQLite/upload paths to the project root.
- Write SQLite `PRAGMA user_version = 1` as a Phase 1 schema marker without
  implementing later-phase domain entities early.
- Validate the complete frontend health schema before showing an online state.
- Use a real JSON formatter and retain LLM secrets only in backend configuration.

### Commands executed

```text
python -m venv .venv
pip install -r requirements.txt
python scripts/init_db.py
pytest -v
pytest -v --cov=app --cov=frontend --cov-report=term-missing
uvicorn app.main:app --host 127.0.0.1 --port 8000
GET http://127.0.0.1:8000/health
streamlit run frontend/Home.py --server.address 127.0.0.1 --server.port 8501
GET http://127.0.0.1:8501/_stcore/health
Streamlit AppTest for frontend/Home.py
```

### Tests executed

Fifteen tests across unit and integration suites, all offline with fake LLM
configuration. Live smoke checks made no LLM provider call.

### Test results

- `15 passed` on Python 3.11.9.
- 89% total coverage across `app` and `frontend`.
- SQLite initialized successfully; default file size 4096 bytes.
- Backend `/health`: HTTP 200 with the documented four-field response.
- Streamlit: HTTP 200, internal health `ok`, Home rendered `Backend is online.`
  with no exception.
- One non-failing upstream `Starlette TestClient`/`httpx` deprecation warning.

### Known issues

- PDF ingestion, Knowledge Unit processing, questions/evaluation, adaptive
  learning, and Tutor Agent execution remain intentionally pending.
- Visual browser inspection was unavailable; Streamlit server health and
  AppTest covered the executable Phase 1 UI path.

### Next step

Begin Phase 2 document processing from the contracts in `docs/03`,
`docs/06`, `docs/07`, and `docs/09`.
