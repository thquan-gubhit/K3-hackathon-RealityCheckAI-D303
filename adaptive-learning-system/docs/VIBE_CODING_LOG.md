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

## 2026-07-30 — Phase 6 hardening and MVP v1.0

### Goal

Close the local MVP with stable framework-level errors, request correlation,
log/secret protections, reproducible demo data, cross-platform verification,
and complete documentation traceability.

### Implemented

- Added safe generated/preserved `X-Request-ID` values to every response and
  error log.
- Normalized Pydantic validation, route/method, application, and unexpected
  failures into the documented error envelope.
- Added credential-pattern redaction and 4,000-character bounds to structured
  log message/exception fields.
- Added static guards against logging page/source/rubric/key fields and against
  committing local `.env`, SQLite, upload, or Streamlit secret artifacts.
- Added `scripts/seed_demo.py`: an idempotent offline seed for one parsed
  document, three Knowledge Units, and nine immutable questions.
- Added Markdown-link/fenced-block checks and a GitHub Actions Python 3.11
  matrix for Windows, Ubuntu, and macOS.
- Published project/API version 1.0.0 and synchronized README, API spec,
  runbook, test plan, TODO, progress, and hardening documentation.

### Verification

```text
pytest tests/unit/test_logging.py tests/integration/test_error_contracts.py -q
→ 5 passed

pytest tests/integration/test_seed_demo.py -q
→ 1 passed

pytest -q
→ 109 passed, 1 upstream TestClient deprecation warning

pytest -q --cov=app --cov=frontend --cov-report=term-missing
→ total coverage 77%

MVP smoke
→ health/request ID, seeded 3×3 assessment map, stable 404, and network
  frontend/backend all passed
```

### Remaining production gaps

Authentication, TLS termination, rate limiting, migrations, encrypted-at-rest
uploads, background jobs, and backup/restore remain outside the local MVP.

## 2026-07-30 — One-upload Auto Learning experience

### Request

Keep the existing step-by-step pages, but add one page where selecting a PDF
automatically uploads it, creates the Knowledge Map, starts a learning session,
and loads the first question. Show the KU beside all source slides assigned to
it, such as slides 1–4 for KU1 and slides 5–10 for KU2.

### Implemented

- Added `frontend/pages/5_Auto_Learning.py` without changing the existing pages.
- File SHA-256 state prevents upload/process calls from repeating on Streamlit
  reruns.
- The first KU session and question are prepared automatically; changing KU
  creates its session/question without reprocessing the document.
- All source pages assigned to the KU are rendered vertically in the left
  column, with lesson summary/objectives/concepts/misconceptions on the right.
- Answer submission remains explicit; feedback, mastery, and the next question
  load in the same page.
- Pipeline failures retain completed stages and expose a scoped retry action.

### Verification

```text
pytest tests/integration/test_frontend_auto_learning.py -q
→ 1 passed

pytest -q
→ 110 passed, 1 upstream TestClient deprecation warning
```

## 2026-07-30 — Administrative-slide coverage fix

### Problem

`B1 - ND.pdf` repeatedly failed `INVALID_SOURCE_COVERAGE`. Offline inspection
showed 22 extracted pages, while slide 22 contained only an exercise heading,
instructor email, and page number. The old segmenter treated it as standalone
learning content, but it did not warrant an independent KU.

### Fix

- Added conservative deterministic detection for very short administrative,
  closing, exercise-title, Q&A, and reference slides.
- Email addresses and page numbers do not count as learning words.
- Marker matching alone is insufficient: pages longer than 12 semantic words
  remain readable, preventing short academic slides from being excluded merely
  because they are short.
- Each excluded page retains an explicit reason in coverage evidence.
- Added safe logging of missing/unexpected page numbers when bounded coverage
  refinement is exhausted.

### Verification

```text
B1 - ND.pdf offline segmentation
→ pages 1–21 readable
→ page 22 explicitly excluded as administrative

pytest -q
→ 112 passed, 1 upstream TestClient deprecation warning
```

### Follow-up from real retry evidence

The next live retry showed the model omitted different substantive example
slides on each run: first `16, 17, 21`, then `9–12, 21`. This proved that
administrative exclusion alone was insufficient.

A bounded deterministic repair now groups consecutive missing pages immediately
after each provider response, ranks existing KUs using semantic token overlap
and original page proximity, and assigns only groups that overlap the selected
KU or are explicitly marked as examples/exercises. Unrelated substantive groups
still use bounded LLM refinement. A persistent-gap integration fake omits page
3 in the first provider response and verifies that the persisted map reaches
100% coverage without a second provider call.

```text
pytest -q
→ 113 passed, 1 upstream TestClient deprecation warning
```

## 2026-07-30 — Source-language consistency

### Problem

The source-grounding prompts did not explicitly bind generated content to the
language used by the slides, so a provider could default Knowledge Units,
questions, or feedback to English.

### Fix

- Added one shared source-language policy to Knowledge Unit extraction and
  refinement, question/rubric generation, answer evaluation, and Tutor Agent
  prompts.
- The dominant language carrying the slide's instructional meaning is now the
  authoritative output language. Isolated technical terms, citations, proper
  nouns, formulas, and code do not cause a language switch.
- Evaluation evidence and feedback stay in the slide language even when the
  learner answers in another language.
- JSON fields, identifiers, action names, and enum values remain unchanged so
  structured-output parsing stays stable.

### Verification

```text
pytest tests/unit/test_llm_prompt_language_policy.py \
  tests/integration/test_document_processing_api.py \
  tests/integration/test_full_learning_and_agent_flow.py -q
→ 11 passed, 1 upstream TestClient deprecation warning

pytest -q
→ 118 passed, 1 upstream TestClient deprecation warning
```
