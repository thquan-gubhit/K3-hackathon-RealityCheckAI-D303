# Architecture Decision Records

> **Delivery status:** These decisions are accepted as the MVP baseline. Phase annotations distinguish implemented foundation choices from later-phase design.

## ADR-001 — Use workflows as the backbone

### Status

Accepted; workflow implementations begin in Phase 2.

### Context

Document processing, question generation, evaluation, and adaptive learning have known steps and validation gates. A single autonomous agent would make normal execution difficult to test and bound.

### Decision

Implement explicit workflows for normal pipelines. Use deterministic rules for policy, narrow LLM calls for semantic tasks, and the Tutor Agent only for eligible exceptions.

### Alternatives

- One autonomous agent controlling the application.
- Endpoint handlers directly chaining services and LLM calls.

### Consequences

Execution is predictable and testable, but workflow transition code and typed intermediate results must be maintained.

## ADR-002 — Use a local modular monolith

### Status

Accepted; Phase 1 foundation implemented.

### Context

The MVP must run locally and be easy to demonstrate. Distributed infrastructure would add operational cost without proving product value.

### Decision

Use Python 3.11, FastAPI, Streamlit, SQLite, SQLAlchemy, and Pydantic in one repository with strict internal layer boundaries.

### Alternatives

- Separate frontend/backend services with a production database.
- A single Streamlit script containing business logic.

### Consequences

Local setup is small and debuggable. SQLite concurrency and Streamlit styling are acceptable MVP limits; modular boundaries must be enforced in code review.

## ADR-003 — Use typed environment configuration

### Status

Accepted; Phase 1 implemented.

### Context

Provider endpoints, model names, credentials, ports, database paths, and policy thresholds vary by operator and must not be hard-coded.

### Decision

Load settings with `pydantic-settings` from environment variables and `.env`. Validate required runtime LLM values at startup, resolve local paths from the project root, and wrap secrets in secret-aware types.

### Alternatives

- Constants in source code.
- Untyped `os.getenv` calls spread across modules.

### Consequences

Misconfiguration fails early with actionable variable names. Local startup requires non-empty provider values even though Phase 1 does not call an LLM.

## ADR-004 — Use SQLite behind SQLAlchemy

### Status

Accepted; Phase 1 engine/session/bootstrap implemented. Domain entities are later-phase work.

### Context

The MVP needs durable local history without operating an external database.

### Decision

Use SQLite through SQLAlchemy repositories and sessions. Keep domain code independent of raw SQL and enable explicit indexes/constraints as entities are added.

### Alternatives

- In-memory state.
- JSON files.
- PostgreSQL from the first phase.

### Consequences

Setup is minimal and state is inspectable. Write concurrency is limited, and future schema changes will need a migration strategy.

## ADR-005 — Validate every LLM output with Pydantic

### Status

Accepted design; implementation begins in Phase 2.

### Context

Generated Knowledge Units, questions, rubrics, evaluations, and actions must have reliable shapes before rules or persistence use them.

### Decision

Expose one OpenAI-compatible adapter method that generates a declared Pydantic response model. Retry invalid JSON/schema output only within configured limits.

### Alternatives

- Parse free-form Markdown.
- Trust provider-native JSON without domain validation.

### Consequences

Downstream code receives typed data and failures are explicit. Prompt schemas and Pydantic models must evolve together.

## ADR-006 — Generate immutable rubrics before learner answers

### Status

Accepted and implemented in Phase 3.

### Context

Changing assessment criteria after seeing an answer creates biased and irreproducible scoring.

### Decision

Generate and persist the reference answer and rubric with the question before it is shown. Evaluation always uses that stored version.

### Alternatives

- Generate a rubric during evaluation.
- Compare answers only through embedding similarity.

### Consequences

Evaluation is auditable and stable. Question generation costs more upfront and rubric versions must be retained.

## ADR-007 — Keep the Tutor Agent optional, bounded, and allow-listed

### Status

Accepted and implemented in Phase 5.

### Context

Some learning failures need multi-step adaptation, but an unrestricted agent conflicts with safety, reproducibility, and the local MVP scope.

### Decision

Gate activation with deterministic rules and `AGENT_ENABLED`; limit steps with `AGENT_MAX_STEPS`; expose only registered service-backed tools; persist redacted traces; retain deterministic remediation when disabled.

### Alternatives

- No adaptive tutor.
- An always-on agent with unrestricted tools.

### Consequences

Exceptional cases receive flexible support within auditable bounds. Policy, tool schemas, stop conditions, and disabled behavior require dedicated tests.

## ADR-008 — Commit extraction evidence before semantic map generation

### Status

Accepted and implemented in Phase 2.

### Context

PDF parsing is deterministic and local, while Knowledge Unit generation depends
on a fallible OpenAI-compatible LLM. Losing parsed pages after a provider failure
would make diagnosis and retry less useful.

### Decision

Persist the `processing` transition and page extraction before the LLM call.
Replace the Knowledge Map and transition to `ready` in one later transaction.
On a bounded parse, LLM, rule, or database failure, retain pages and record
`failed` when persistence remains available.

### Alternatives

- Keep the entire workflow in one long transaction.
- Save partial or unvalidated Knowledge Units.

### Consequences

Retries retain durable extraction evidence and invalid maps are never published.
A failed document may contain parsed pages internally, while the API blocks its
Knowledge Map until a successful reprocess.
