# Business Requirements

> **Delivery status:** Requirements are baselined in Phase 1. Product behavior described below is the MVP contract for Phases 2–5 and is not an implementation claim.

## Actors

| Actor | Goal | MVP permissions |
| --- | --- | --- |
| Learner | Study a document through active recall | Upload, process, study, answer, inspect feedback and progress |
| Local operator | Configure and run the application | Manage `.env`, initialize the database, start services, inspect logs |
| LLM provider | Perform bounded semantic transformations | Receive scoped context and return schema-valid outputs |
| Tutor Agent | Handle configured learning exceptions | Use allow-listed tutoring tools only when enabled and triggered |

## User stories

| ID | Story | Target phase |
| --- | --- | --- |
| US-001 | As a learner, I want to upload a PDF and see whether it can be processed. | 2 |
| US-002 | As a learner, I want a Knowledge Map so I can choose a coherent topic. | 2 |
| US-003 | As a learner, I want the lesson hidden after reading so recall is genuine. | 3 |
| US-004 | As a learner, I want Recall, Explain, and Apply questions grounded in the source. | 3 |
| US-005 | As a learner, I want feedback separated into correct, missing, incorrect, and misconception points. | 3 |
| US-006 | As a learner, I want my next activity to adapt to demonstrated understanding. | 4 |
| US-007 | As a learner, I want progress by unit and cognitive dimension. | 4 |
| US-008 | As a struggling learner, I want a different explanation or scaffold when normal remediation fails. | 5 |
| US-009 | As an operator, I want the normal workflow to work with the agent disabled. | 5 |
| US-010 | As an operator, I want actionable startup errors without exposing secrets. | 1 |

## Business rules

- **BR-001 — Source grounding:** generated learning content must be answerable from the uploaded document and must retain source-page references.
- **BR-002 — Knowledge Unit size:** a valid unit has 1–3 learning objectives, 2–7 key concepts, and an estimated 2–10 minutes of reading.
- **BR-003 — Stable assessment:** the reference answer and rubric are created before the learner answer and are never rewritten in response to it.
- **BR-004 — Structured evaluation:** every accepted evaluation reports scores in `[0, 1]`, evidence categories, feedback, confidence, and a recommended next action.
- **BR-005 — Conservative mastery:** `MASTERED` requires threshold, evidence count, application evidence, and no unresolved critical misconception.
- **BR-006 — Deterministic control:** workflow steps and policy decisions are code-controlled; the LLM supplies semantic candidates, not final policy authority.
- **BR-007 — Bounded agent:** the Tutor Agent is optional, allow-listed, auditable, and limited to `AGENT_MAX_STEPS`.
- **BR-008 — Local-first history:** documents, attempts, mastery, misconceptions, and traces are stored in SQLite for the MVP.
- **BR-009 — Secret handling:** credentials come from environment configuration and are never returned to the UI or logs.
- **BR-010 — Retry limits:** invalid LLM output may be retried only up to the configured limit.

## Functional requirements

| ID | Requirement | Target phase |
| --- | --- | --- |
| FR-001 | Load and validate application configuration from `.env`. | 1 |
| FR-002 | Initialize the SQLite database and expose `GET /health`. | 1 |
| FR-003 | Provide a Streamlit home page that reports backend reachability. | 1 |
| FR-004 | Validate, store, and parse one PDF into page records. | 2 |
| FR-005 | Generate and rule-validate 3–10 Knowledge Units. | 2 |
| FR-006 | Return a Knowledge Map with source coverage and prerequisites. | 2 |
| FR-007 | Generate validated question candidates, reference answers, and rubrics. | 3 |
| FR-008 | Evaluate free-text answers using the stored rubric. | 3 |
| FR-009 | Persist answer attempts and structured feedback. | 3 |
| FR-010 | Create learning sessions and select the next activity through rules. | 4 |
| FR-011 | Update and display mastery by unit and cognitive dimension. | 4 |
| FR-012 | Trigger, run, stop, and trace the Tutor Agent under policy. | 5 |

## Non-functional requirements

| Area | Requirement |
| --- | --- |
| Portability | Run locally on Windows and Linux/macOS with Python 3.11. |
| Security | No committed secrets; no API keys or full documents in normal logs. |
| Reliability | Bounded timeout, retry, workflow, and agent step counts. |
| Auditability | Persist source pages, rubric used, rule outcome, evaluation, and agent trace metadata. |
| Testability | Mock all LLM calls in default tests; unit-test every important deterministic rule. |
| Maintainability | Preserve the dependency direction `API → Workflow → Service → Rule/Agent → Repository → Database`. |
| Validation | Parse every LLM structured output through Pydantic. |
| Performance | Keep interactive local requests responsive; isolate long document processing as an explicit operation. |
| Accessibility | Use clear labels, status messages, and text feedback; do not communicate progress by color alone. |

## Acceptance criteria

### Phase 1

- The backend starts with valid configuration and `GET /health` returns HTTP 200.
- The Streamlit home page can check the configured backend URL.
- The database initialization command completes against the configured SQLite path.
- Missing required configuration produces a clear remediation message and does not reveal secret values.
- Configuration and health tests pass without calling an external LLM.
- All mandatory Markdown files exist with later-phase behavior clearly marked pending.

### MVP

1. A readable demo PDF uploads and produces at least three valid Knowledge Units.
2. Every unit has an objective, concepts, source pages, and validity status.
3. Recall, Explain, and Apply questions are generated for a unit.
4. The application distinguishes correct, incomplete, and misconception-bearing answers.
5. Mastery changes after each answer and honors minimum evidence rules.
6. A repeated misconception triggers the Tutor Agent when enabled.
7. The agent never exceeds its configured step limit.
8. The application remains usable with `AGENT_ENABLED=false`.

## Requirement traceability convention

Tests should reference requirement or rule IDs in names or docstrings where practical, for example `test_br_005_requires_application_evidence`. Later phases must update this file if behavior changes.

