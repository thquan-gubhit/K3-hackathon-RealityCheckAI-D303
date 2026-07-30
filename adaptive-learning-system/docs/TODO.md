# TODO

> Checked items are implemented and verified where applicable. Phase 1 is
> complete; all product behavior after the foundation remains pending.

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

- [ ] Validate PDF MIME/signature and configured size.
- [ ] Store document metadata safely.
- [ ] Extract page-level text with PyMuPDF.
- [ ] Handle empty/image-only/unreadable PDFs.
- [ ] Persist `Document` and `DocumentPage`.
- [ ] Add OpenAI-compatible structured LLM adapter.
- [ ] Extract 3–10 candidate Knowledge Units.
- [ ] Implement and test split/merge/refinement rules.
- [ ] Validate source coverage and duplicates.
- [ ] Expose document and Knowledge Map endpoints/UI.

### Phase 3 — Questions and evaluation

- [ ] Implement question/reference-answer/rubric schemas.
- [ ] Generate Recall, Explain, and Apply candidates.
- [ ] Validate grounding, objective alignment, clarity, leakage, and duplication.
- [ ] Persist immutable rubric before learner answer.
- [ ] Evaluate free-text answers into all required evidence fields.
- [ ] Handle low confidence with clarification, not severe automatic diagnosis.
- [ ] Persist answer attempts and feedback.

### Phase 4 — Adaptive learning

- [ ] Create and persist learning sessions.
- [ ] Implement deterministic next-question rules and caps.
- [ ] Implement mastery formula, difficulty, evidence weighting, and clamp.
- [ ] Enforce all `MASTERED` predicates.
- [ ] Track active/resolved misconceptions.
- [ ] Implement deterministic remediation.
- [ ] Add progress endpoints and Streamlit dashboard.

### Phase 5 — Tutor Agent

- [ ] Implement absolute `AGENT_ENABLED` gate.
- [ ] Implement and test agent trigger rules.
- [ ] Add allow-listed, service-backed tools.
- [ ] Add validated function-call/JSON action schema.
- [ ] Enforce `AGENT_MAX_STEPS` and all stop conditions.
- [ ] Persist redacted activation and step traces.
- [ ] Return `AGENT_DISABLED` while preserving normal workflow.

### Phase 6 — Hardening

- [ ] Run complete unit, integration, and acceptance suites.
- [ ] Complete stable error-code coverage and structured logging.
- [ ] Verify no secrets or full source documents appear in logs/repository.
- [ ] Add demo fixtures and seed data.
- [ ] Verify Windows and Linux/macOS runbooks.
- [ ] Complete README/docs traceability and final demo smoke test.

## P1 — Should have

- [ ] Add database migrations once the domain schema stabilizes.
- [ ] Add operation/request IDs to logs and errors.
- [ ] Add a visible processing-state timeline and safe retry controls.
- [ ] Add export/import of local learning history.
- [ ] Add automated Markdown link and Mermaid syntax checks.
- [ ] Add accessibility review for Streamlit pages.

## P2 — After MVP

- [ ] Production deployment and production database.
- [ ] Complete authentication and multi-user authorization.
- [ ] Advanced OCR for scanned PDFs.
- [ ] Advanced spaced repetition.
- [ ] Dedicated vector database where justified by measured need.
- [ ] Video/audio ingestion.
- [ ] Fine-tuning or model-specific optimization.
- [ ] Multi-agent orchestration.
