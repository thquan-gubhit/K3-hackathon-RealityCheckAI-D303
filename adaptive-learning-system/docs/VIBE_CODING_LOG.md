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

## 2026-07-30 15:25 +07:00 — Phase 2 document processing

### Goal

Implement the complete Phase 2 path from safe PDF upload through persisted
Knowledge Map, without starting Phase 3 question/evaluation work.

### Files created

- Document, page, and Knowledge Unit models/schemas/repositories.
- PDF parser, deterministic segmenter, document upload service, KU service, and
  document-processing workflow.
- OpenAI-compatible LLM client/adapter, prompts, and structured-output parser.
- Document and Knowledge Unit API routers plus stable application errors.
- Streamlit Upload Document and Knowledge Map pages.
- `scripts/create_demo_pdf.py` and the generated three-page ML fixture.
- Phase 2 unit/integration/frontend tests.

### Files modified

- Application bootstrap, database helpers/schema marker, model exports, frontend
  API client, dependencies, requirements, README, and Phase 2 design/run docs.

### Technical decisions

- Keep API handlers transport-only and run semantic work through the explicit
  workflow.
- Store PDFs under server-generated UUID names and never expose storage paths.
- Persist parsed pages before the external-compatible LLM call; publish the map
  only after all deterministic gates pass.
- Treat LLM candidate IDs as temporary references and translate prerequisites
  to persisted UUIDs.
- Keep default tests completely offline with injected fake/scripted LLMs.

### Commands executed

```text
pip install reportlab
python scripts/create_demo_pdf.py
pytest -q
pytest -q --cov=app --cov-report=term-missing
python -m compileall -q app frontend scripts tests
python -m pip check
```

The generated fixture was rendered to three PNG pages with PyMuPDF because
Poppler was not available; all pages were visually inspected.

### Tests executed

- PDF parsing, upload validation, segmentation, structured-output retries, KU
  split/merge/coverage/duplicate rules, frontend client/pages, database, API,
  and the full PDF-to-persisted-map workflow.

### Test results

- `69 passed` on Python 3.11.9.
- 75% statement/branch coverage across `app`.
- Demo integration: 3 parsed pages, 3 valid KUs, 100% readable-page coverage.
- Compile check passed.
- `pip check`: no broken requirements.
- One non-failing upstream Starlette TestClient/httpx deprecation warning.

### Known issues

- Processing is synchronous.
- Image-only PDFs require out-of-scope OCR.
- No real provider call was made during verification; live behavior depends on
  operator `.env` configuration.
- Question/evaluation, adaptive learning, and Tutor Agent remain pending.

### Next step

Begin Phase 3 question generation, immutable rubrics, and answer evaluation.

## 2026-07-30 — Phases 3–5 learning loop and bounded Tutor Agent

### Prompt/request

Continue with Phases 3, 4, and 5 from the existing Phase 2 baseline.

### Implemented

- Added persisted source-grounded questions with mandatory Recall, Explain, and
  Apply coverage, deterministic validation, private reference answers, and
  immutable versioned rubrics.
- Added structured answer evaluation with correct/missing/incorrect evidence,
  misconceptions, dimension scores, confidence-safe clarification, and stored
  attempts.
- Added learning sessions, deterministic next-question/remediation selection,
  difficulty-adjusted mastery, diminishing duplicate evidence, conservative
  mastery gates, misconception aggregation, progress APIs, and Streamlit study
  and dashboard pages.
- Added an optional Tutor Agent with absolute configuration gate, explicit
  trigger rules, validated action schema, service-backed allow-listed tools,
  maximum-step enforcement, and redacted persisted traces.
- Registered the Phase 3–5 API routers and advanced SQLite `user_version` to 5.

### Decisions

- Public question responses never expose reference answers or rubrics.
- Low-confidence evaluation requests clarification and cannot automatically add
  a severe misconception.
- The normal workflow remains deterministic and usable when the agent is
  disabled; agent execution is an exception path only.
- Test doubles are selected by typed response schema and never call a provider.

### Verification

```text
pytest -q --cov=app --cov=frontend --cov-report=term-missing
→ 99 passed, 1 upstream TestClient deprecation warning, total coverage 76%

pytest tests/unit/test_frontend_api_client.py \
  tests/integration/test_frontend_learning_pages.py -q
→ 14 passed
```

The end-to-end acceptance fixture covers PDF processing, three generated
question types, strong/incomplete/misconception evaluation, mastery persistence,
repeated-misconception activation, the agent step cap, trace redaction, and
agent-disabled normal operation.

### Limitations / next task

Processing and LLM calls remain synchronous. Live-provider quality was not
tested in the offline suite. Continue with Phase 6 hardening, migration strategy,
cross-platform smoke tests, security/log review, and final packaging.

## 2026-07-30 — Source coverage refinement bug fix

### Problem

An 11-page readable PDF failed with `INVALID_SOURCE_COVERAGE` when the initial
LLM Knowledge Map omitted one or more page references. The workflow stopped
immediately even though bounded refinement rounds were configured.

### Fix

- Added a map-level coverage refinement prompt containing the current map,
  expected readable pages, missing/unexpected pages, and source segments.
- The prompt requires semantic revision of affected units instead of attaching
  unrelated citations.
- Updated document processing to retry coverage within
  `KU_MAX_REFINEMENT_ROUNDS`, validate the complete revised map again, and keep
  the original terminal error if bounded repair still fails.
- Added an offline integration fixture that omits page 3 on the first response
  and restores it on the refinement response.

### Verification

```text
pytest tests/integration/test_document_processing_api.py -q
→ 3 passed

pytest -q
→ 100 passed, 1 upstream TestClient deprecation warning
```
