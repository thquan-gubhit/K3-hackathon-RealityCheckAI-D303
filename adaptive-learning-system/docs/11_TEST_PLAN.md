# Test Plan

> **Delivery status:** Phases 1–6 have 122 passing tests on Python 3.11.9,
> including the full fake-LLM learning loop and Phase 6 hardening gates.

## Strategy

Use a test pyramid:

1. many fast unit tests for typed configuration, pure rules, calculations, validators, and adapters;
2. focused integration tests for API/workflow/repository boundaries with temporary SQLite storage; and
3. a small acceptance suite for the local learner flow.

Default tests must be deterministic, offline, and free of real provider credentials.

## Test environments

| Environment | Database | LLM | Purpose |
| --- | --- | --- | --- |
| Unit | None or in-memory fixture | Stub/fake | Pure behavior and boundaries |
| Integration | Temporary SQLite file | Scripted mock | API-to-persistence workflow |
| Local acceptance | Disposable local database | Mock by default; live only by explicit opt-in | Demo-flow verification |

Do not call a real LLM in CI or in the default `pytest` command.

## Phase 1 tests

| Area | Coverage |
| --- | --- |
| Configuration | Environment/dotenv parsing, typed values, host debug alias, project-root paths, secret redaction |
| Startup validation | Missing `LLM_API_KEY`, `LLM_BASE_URL`, and `LLM_MODEL` produce actionable names without exposing values |
| Database | SQLite initialization writes the schema marker and accepts a query |
| Health API | `GET /health` returns HTTP 200 and the stable response contract under test configuration |
| Frontend client | URL selection, offline handling, malformed URL, and false-green response rejection |
| Streamlit Home | Page executes without exception and renders the connected-backend state |
| Logging | Quotes/newlines remain valid structured JSON |

Current locations:

```text
tests/unit/test_config.py
tests/unit/test_frontend_api_client.py
tests/unit/test_logging.py
tests/integration/test_database.py
tests/integration/test_frontend_home.py
tests/integration/test_health.py
```

The Phase 1 suite contains **15 tests** and all pass on Python 3.11.9. The
coverage run reports **89% total statement/branch coverage** across `app` and
`frontend`. The only emitted warning is a non-failing upstream
`Starlette TestClient`/`httpx` deprecation warning.

## Unit tests for Phases 3–5

| Target | Required cases | Phase |
| --- | --- | --- |
| KU split rules | Objective, concept, and reading-time thresholds; exact boundaries | 2 |
| KU merge rules | Small fragment, example-only, no independent question, adjacent overlap | 2 |
| Structured outputs | Valid/invalid KU, question, rubric, and evaluation JSON | 2–3 |
| Prompt language policy | Slide language controls KU, question, rubric, feedback, and tutor output language | 2–5 |
| Question validation | Grounding, objective mismatch, answer leak, ambiguity, external facts, duplicate | 3 |
| Question selection | First recall, low recall scaffold, score bands, application gap, cap | 4 |
| Mastery | Formula, difficulty, clamp, repeated evidence weights, all mastery predicates | 4 |
| Agent triggers | Disabled gate, repeat count, failed remediation, score gap | 5 |
| Agent runner | Allow list, schema retry, stop conditions, exact maximum steps | 5 |

Every rule in `07_RULE_ENGINE.md` should have a corresponding test named in its `Test` column.

## Integration tests

### Phase 1

```text
FastAPI lifespan with test settings
→ GET /health
→ validate status/app_name/environment/database response
```

### Target pipeline

```text
PDF fixture
→ page extraction
→ Knowledge Units
→ question/reference answer/rubric
→ answer evaluation
→ mastery update
→ next-action selection
```

Integration assertions include:

- source pages survive each transformation;
- a rubric is stored before answer submission;
- invalid LLM JSON exhausts only bounded retries;
- a failed evaluation does not update mastery;
- agent-disabled mode uses deterministic remediation; and
- persistence can reload the same session state.

## Acceptance tests

| ID | Scenario | Expected result | Status |
| --- | --- | --- | --- |
| AT-001 | Start configured backend and request `/health` | HTTP 200 with stable health payload | Passed — local smoke test |
| AT-002 | Execute Streamlit home with backend running | Connectivity and Phase 1 status shown | Passed — server health + AppTest |
| AT-003 | Upload readable demo PDF | Upload succeeds | Passed — integration |
| AT-004 | Process demo PDF | At least three valid KUs with objectives/concepts/pages | Passed — 3 KUs, 100% coverage |
| AT-005 | Generate questions | Recall, Explain, and Apply are available | Passed |
| AT-006 | Submit strong, incomplete, and misconception answers | Feedback distinguishes all three | Passed |
| AT-007 | Answer several questions | Mastery changes and respects evidence gates | Passed |
| AT-008 | Repeat one misconception | Agent triggers when enabled | Passed |
| AT-009 | Reach agent step limit | Agent stops at or before configured maximum | Passed |
| AT-010 | Disable agent | Normal learning workflow remains usable | Passed |
| AT-011 | Select one PDF in Auto Learning | Upload, map, session, and first question load automatically | Passed |
| AT-012 | Change KU in Auto Learning | New session/question loads without re-upload or re-process | Passed |
| AT-013 | Open `/vlearn/` from the backend | VLearn reference UI and integration assets load | Passed |
| AT-014 | Preflight from the local prototype origin | Explicit local origin is allowed without wildcard CORS | Passed |

## Mock strategy

- Define an LLM client interface and inject a scripted fake.
- Key fake scenarios by prompt/task name, not by brittle full prompt text.
- Include valid response, malformed JSON, schema mismatch, timeout, retry-then-success, and insufficient-context fixtures.
- Never use a committed real API key.
- Freeze timestamps or assert shapes instead of exact wall-clock values.
- Use `tmp_path` for SQLite files and upload directories.

## Fixtures

The delivered fixture set includes:

- a short machine-learning PDF/text fixture;
- one valid overfitting KU;
- a correct answer;
- an answer missing a required point;
- an answer containing the target misconception; and
- a scripted repeated-misconception history.

Phase 2 provides `tests/fixtures/demo_machine_learning.pdf`, generated
deterministically by `scripts/create_demo_pdf.py`. Its three readable pages cover
generalization/data splits, overfitting evidence, and regularization/early
stopping. The default integration test injects a fake structured LLM and proves:

```text
multipart upload -> 3 parsed pages -> 3 valid KUs -> persisted Knowledge Map
```

No default test contacts a real provider.

## Commands

From the project root after installing Python 3.11 and dependencies:

```bash
pytest -v
pytest -v tests/unit
pytest -v tests/integration
pytest --cov=app --cov=frontend --cov-report=term-missing
```

## Exit criteria

- Phase tests run without live network calls.
- All tests in scope pass on Python 3.11.
- Important rules cover both sides and exact values of thresholds.
- No failed/schema-invalid evaluation mutates learning state.
- Any skipped test has a documented reason and owner/phase.
