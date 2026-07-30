# Project Progress

## Current phase

**Phases 1–5 — MVP learning loop: completed and verified.**

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
| 6 — Hardening | Pending | Final cross-phase acceptance, packaging, and production polish |

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

## In progress

None. Phase 6 hardening remains.

## Blocked

None.

## Verification evidence

```text
pytest -q
→ 100 passed, 1 upstream TestClient deprecation warning

tests/integration/test_document_processing_api.py
→ multipart PDF upload
→ 3 parsed and persisted pages
→ 3 valid persisted Knowledge Units
→ readable_pages=3, covered_pages=3, coverage_ratio=1.0

python -m compileall -q app frontend scripts tests
→ passed

python -m pip check
→ No broken requirements found.
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

1. Run Phase 6 security/logging/error-code review.
2. Add a migration tool before changing the stabilized schema further.
3. Verify cross-platform runbooks and the live-provider demo.
4. Complete accessibility and final packaging checks.
