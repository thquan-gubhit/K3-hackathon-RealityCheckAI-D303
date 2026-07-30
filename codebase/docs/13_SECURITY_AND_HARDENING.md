# Security and Hardening

> **Delivery status:** Phase 6 is implemented and locally verified for MVP
> v1.0. Cross-platform regression is enforced by the repository CI matrix.

## Request and error safety

- Every response includes `X-Request-ID`; a safe caller-supplied value is
  preserved and invalid input is replaced with a UUID.
- Application, validation, route, method, and unexpected errors use the same
  `{"error": {...}}` envelope.
- Validation responses include only field location and error type, never the
  rejected input value.
- Unexpected exceptions return `INTERNAL_SERVER_ERROR`; exception messages and
  provider details are not returned.

## Logging safety

- Application logs are one-line JSON.
- Credential-shaped `Authorization`, bearer token, API key, access token,
  password, and OpenAI-style key values are redacted.
- Individual message/exception fields are bounded to 4,000 characters.
- Static tests reject logger calls that include raw/cleaned page text, source
  context, reference answers, or the configured LLM key.

## Local-data boundary

The MVP stores document pages, rubrics, attempts, mastery, misconceptions, and
agent traces in the configured SQLite database. `.env`, SQLite files, upload
contents, Streamlit secrets, coverage output, and virtual environments are
ignored by Git. Public question responses exclude reference answers and rubrics.

The application has no authentication. Bind to `127.0.0.1` unless access by
trusted devices on a private LAN is intentional. Never expose the development
server directly to the public Internet.

## Offline demo seed

```bash
python scripts/seed_demo.py
```

The command idempotently parses the committed three-page fixture locally and
creates one ready document, three Knowledge Units, and nine immutable questions.
It does not call an LLM provider. Learner answer evaluation still requires the
configured provider.

## Automated gates

```bash
python -m compileall -q app frontend scripts tests
python -m pip check
pytest -q
pytest --cov=app --cov=frontend --cov-report=term-missing
git diff --check
```

The GitHub Actions workflow runs compile, dependency, and test gates on Python
3.11 for Windows, Ubuntu, and macOS. Default tests use fake LLMs and temporary
SQLite databases, so they do not contact a provider or mutate local app data.

## Remaining production gaps

- No authentication, authorization, rate limiting, or TLS termination.
- No database migration framework or backup/restore command.
- Synchronous PDF/LLM processing can hold a request for provider timeout length.
- Uploaded documents and local SQLite history are not encrypted at rest by the
  application.
- The upstream Starlette TestClient/httpx deprecation warning remains
  non-failing.
