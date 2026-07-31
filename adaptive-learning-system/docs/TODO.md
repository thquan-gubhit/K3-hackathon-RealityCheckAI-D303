# TODO

> Checked items are implemented and verified where applicable. Phases 1–6 are
> complete for local MVP v1.0.

## P0 — Required for MVP

### Phase 1 — Foundation

- [x] Create modular project/package structure.
- [x] Add dependency and pytest configuration.
- [x] Add `.env.example` and secret-safe typed settings.
- [x] Add SQLAlchemy/SQLite bootstrap and initialization command.
- [x] Add FastAPI `GET /health`.
- [x] Add Streamlit home and backend health client.
- [x] Author configuration, health, and frontend-client tests.
- [x] Create mandatory Markdown documentation.
- [x] Run Phase 1 tests and smoke tests on Python 3.11.

### Phase 2 — Document processing

- [x] Validate PDF MIME/signature and configured size.
- [x] Store document metadata safely.
- [x] Extract page-level text with PyMuPDF.
- [x] Handle empty/image-only/unreadable PDFs.
- [x] Persist `Document` and `DocumentPage`.
- [x] Add OpenAI-compatible structured LLM adapter.
- [x] Extract 3–10 candidate Knowledge Units.
- [x] Implement and test split/merge/refinement rules.
- [x] Validate source coverage and duplicates.
- [x] Expose document and Knowledge Map endpoints/UI.

### Phase 3 — Questions and evaluation

- [x] Implement question/reference-answer/rubric schemas.
- [x] Generate Recall, Explain, and Apply candidates.
- [x] Validate grounding, objective alignment, clarity, leakage, and duplication.
- [x] Persist immutable rubric before learner answer.
- [x] Evaluate free-text answers into all required evidence fields.
- [x] Handle low confidence with clarification, not severe automatic diagnosis.
- [x] Persist answer attempts and feedback.

### Phase 4 — Adaptive learning

- [x] Create and persist learning sessions.
- [x] Implement deterministic next-question rules and caps.
- [x] Implement mastery formula, difficulty, evidence weighting, and clamp.
- [x] Enforce all `MASTERED` predicates.
- [x] Track active/resolved misconceptions.
- [x] Implement deterministic remediation.
- [x] Add progress endpoints and Streamlit dashboard.

### Phase 5 — Tutor Agent

- [x] Implement absolute `AGENT_ENABLED` gate.
- [x] Implement and test agent trigger rules.
- [x] Add allow-listed, service-backed tools.
- [x] Add validated function-call/JSON action schema.
- [x] Enforce `AGENT_MAX_STEPS` and all stop conditions.
- [x] Persist redacted activation and step traces.
- [x] Return `AGENT_DISABLED` while preserving normal workflow.

### Phase 6 — Hardening

- [x] Run complete unit, integration, and acceptance suites.
- [x] Complete stable error-code coverage and structured logging.
- [x] Verify no secrets or full source documents appear in logs/repository.
- [x] Add demo fixtures and seed data.
- [x] Add Windows, Ubuntu, and macOS CI verification for runbook commands.
- [x] Complete README/docs traceability and final demo smoke test.

## P1 — Should have

- [ ] Add database migrations once the domain schema stabilizes.
- [x] Add operation/request IDs to logs and errors.
- [x] Add an automatic three-stage processing timeline and safe retry controls.
- [ ] Add export/import of local learning history.
- [x] Add automated Markdown link and fenced-block syntax checks.
- [x] Add accessibility review for Streamlit control labels and text feedback.
- [ ] Move synchronous document processing to a background job if measured
  document/provider latency harms the local UX.

## P2 — After MVP

- [ ] Production deployment and production database.
- [ ] Complete authentication and multi-user authorization.
- [ ] Advanced OCR for scanned PDFs.
- [ ] Advanced spaced repetition.
- [ ] Dedicated vector database where justified by measured need.
- [ ] Video/audio ingestion.
- [ ] Fine-tuning or model-specific optimization.
- [ ] Multi-agent orchestration.
