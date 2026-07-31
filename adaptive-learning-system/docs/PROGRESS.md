# Project Progress

## Current phase

**Phases 1–6 — local MVP v1.0: completed and verified.**

The local MVP now covers PDF-to-Knowledge-Map, source-grounded assessment,
adaptive sessions/mastery, progress UI, and a bounded opt-in Tutor Agent.

## Phase status

| Phase | Status | Notes |
| --- | --- | --- |
| 1 — Project foundation | **Completed and verified** | Config, SQLite, health API, Streamlit Home, tests, docs |
| 2 — Document processing | **Completed and verified** | PDF/pages, structured KU pipeline, rules, map API/UI |
| 3 — Question and evaluation | **Completed and verified** | Validated question/rubric generation and evidence-rich evaluation |
| 4 — Adaptive learning | **Completed and verified** | Sessions, deterministic routing, mastery, misconceptions, progress UI |
| 5 — Tutor Agent | **Completed and verified** | Absolute gate, triggers, bounded runner, allow-list tools, redacted traces |
| 6 — Hardening | **Completed and verified** | Request correlation, safe errors/logs, seed, CI matrix, docs gates |

## Completed

- Added safe multipart PDF validation for extension, media type, signature,
  empty content, and configured size.
- Added UUID-backed `Document`, `DocumentPage`, and `KnowledgeUnit` persistence,
  SQLite foreign keys, constraints/indexes, and schema marker version 2.
- Added PyMuPDF page extraction, text cleanup, heading detection, and stable
  encrypted/empty/unreadable/textless PDF errors.
- Added deterministic heading/size segmentation with explicit blank-page
  exclusions.
- Added an OpenAI-compatible structured LLM adapter with timeout, exponential
  retry budget, Pydantic parsing, safe logging, and no hard-coded provider data.
- Added source-grounded KU prompts, schemas, split/merge/refinement rules,
  source-coverage validation, duplicate validation, and prerequisite ID
  translation.
- Added the synchronous document workflow and all required Phase 2 read/write
  endpoints with stable error envelopes.
- Added Streamlit Upload Document and Knowledge Map pages plus transport helpers.
- Added a deterministic three-page machine-learning PDF fixture and generator.
- Verified the complete demo pipeline using a fake LLM; no default test calls a
  real provider.
- Added Recall, Explain, and Apply generation with source/objective/leakage,
  ambiguity, external-knowledge, and duplicate validation.
- Persisted reference answers and versioned rubrics before exposure; public
  schemas never return either field.
- Added structured answer evidence, confidence-safe clarification, attempts,
  sessions, mastery dimensions, independent evidence, and misconceptions.
- Added deterministic selection/remediation, conservative `MASTERED` gates,
  progress APIs, Study Session, and Progress Dashboard.
- Added an optional Tutor Agent with trigger policy, validated actions,
  service-backed allow-list tools, maximum-step enforcement, and redacted traces.
- Advanced the SQLite schema marker to version 5.
- Added generated/preserved request IDs, stable validation/route/unexpected
  error envelopes, log credential redaction, and bounded log fields.
- Added an idempotent offline seed with one document, three KUs, and nine
  immutable questions.
- Added security/static documentation checks and a Windows–Ubuntu–macOS CI
  matrix for compile, dependency, and offline tests.
- Published package/API version 1.0.0 and completed documentation traceability.
- Added the Auto Learning page: one PDF selection automatically performs
  upload, Knowledge Map processing, session creation, and first-question load.
  It renders every source slide for the selected KU beside its lesson and
  creates a new session automatically when the learner changes KU.
- Fixed coverage validation for short administrative/closing slides. A terminal
  exercise-title/email/page-number slide is explicitly excluded with an audit
  reason instead of forcing the LLM to invent an unrelated Knowledge Unit.
- Added deterministic immediate coverage repair for continuation/example slide
  groups that an LLM omits. Before making another provider call, assignment
  uses semantic token overlap and source-page proximity; unrelated substantive
  groups are refused and continue through bounded LLM refinement.
- Made the dominant instructional language of the source slides authoritative
  across Knowledge Units, questions, reference answers, rubrics, evaluation
  feedback, and learner-facing Tutor Agent output. Schema keys and enum values
  remain unchanged.
- Connected the `codebase/noi-lai-di` VLearn reference UI to the existing
  FastAPI pipeline. The backend now serves `/vlearn/`; one PDF upload drives
  processing, KU navigation, PDF display, session/question creation, answer
  evaluation, mastery feedback, and next-question loading in the VLearn reader.
- Added explicit local-origin CORS support without wildcard access and made the
  host `DEBUG=WARN` mode resolve safely to non-debug startup.
- Fixed VLearn PDF upload startup failures caused by an empty SQLite file. The
  backend launcher now initializes the registered schema before Uvicorn accepts
  requests, while preserving existing tables and records.

## In progress

None.

## Blocked

None.

## Verification evidence

```text
pytest -q
→ 122 passed, 1 upstream TestClient deprecation warning

pytest -q --cov=app --cov=frontend --cov-report=term-missing
→ total coverage 77%

tests/integration/test_document_processing_api.py
→ multipart PDF upload
→ 3 parsed and persisted pages
→ 3 valid persisted Knowledge Units
→ readable_pages=3, covered_pages=3, coverage_ratio=1.0

python -m compileall -q app frontend scripts tests
→ passed

python -m pip check
→ No broken requirements found.

MVP v1.0 smoke
→ health 200 with X-Request-ID
→ demo document ready, 3 units, 3 questions per unit
→ unknown route uses ROUTE_NOT_FOUND with request ID
→ network frontend/backend both return 200
```

The fixture PDF was rendered to PNG and all three pages were visually inspected
for clipping, overlap, and broken glyphs.

## Known limitations

- Processing is synchronous; large documents/provider latency block the request.
- Image-only/scanned PDFs require OCR, which is outside the MVP.
- Live provider behavior depends on operator-supplied `.env` values and was not
  exercised during the offline verification.
- The upstream Starlette TestClient/httpx deprecation warning is non-failing.
- Progress reads create missing default mastery rows for local MVP convenience.
- Agent quality still depends on the configured provider/model; policy and step
  bounds are deterministic.

## Next actions

1. Add a migration tool before changing the stabilized schema further.
2. Add authentication/authorization before any public-network deployment.
3. Move long-running processing to a background worker when measured latency
   justifies it.
4. Add backup/export and restore/import for local learning history.
