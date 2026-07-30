# API Specification

> **Delivery status:** `GET /health` is the only Phase 1 application endpoint. All document, learning, progress, and agent endpoints are contracts for later phases and remain pending.

Base URL for local development: `http://127.0.0.1:8000`.

## Endpoint inventory

| Method | Path | Request | Success response | Common errors | Phase/status |
| --- | --- | --- | --- | --- | --- |
| `GET` | `/health` | None | Health object | `503 SERVICE_UNAVAILABLE` | 1 — completed |
| `POST` | `/documents/upload` | Multipart PDF | `Document` | `INVALID_FILE_TYPE`, `FILE_TOO_LARGE` | 2 — pending |
| `POST` | `/documents/{document_id}/process` | Empty or processing options | Processing result | `DOCUMENT_NOT_FOUND`, `PDF_TEXT_UNAVAILABLE` | 2 — pending |
| `GET` | `/documents` | Query filters | Document list | `DATABASE_ERROR` | 2 — pending |
| `GET` | `/documents/{document_id}` | Path ID | `Document` | `DOCUMENT_NOT_FOUND` | 2 — pending |
| `GET` | `/documents/{document_id}/knowledge-map` | Path ID | Knowledge Unit list/map | `MAP_NOT_READY` | 2 — pending |
| `GET` | `/knowledge-units/{unit_id}` | Path ID | `KnowledgeUnit` | `UNIT_NOT_FOUND` | 2 — pending |
| `GET` | `/knowledge-units/{unit_id}/questions` | Path ID | Question summaries | `UNIT_NOT_FOUND` | 3 — pending |
| `POST` | `/knowledge-units/{unit_id}/generate-questions` | Optional type/count | Accepted questions | `NO_VALID_QUESTION`, `LLM_UNAVAILABLE` | 3 — pending |
| `POST` | `/learning-sessions` | user/document/unit selection | `LearningSession` | `DOCUMENT_NOT_READY` | 4 — pending |
| `GET` | `/learning-sessions/{session_id}` | Path ID | Session state | `SESSION_NOT_FOUND` | 4 — pending |
| `GET` | `/learning-sessions/{session_id}/next-question` | Path ID | Next activity | `NO_NEXT_ACTIVITY` | 4 — pending |
| `POST` | `/learning-sessions/{session_id}/answers` | question ID and answer | Evaluation/mastery | `INVALID_ANSWER`, `EVALUATION_FAILED` | 3–4 — pending |
| `POST` | `/learning-sessions/{session_id}/finish-unit` | Optional unit ID | Updated session | `UNIT_NOT_FINISHABLE` | 4 — pending |
| `GET` | `/progress/{user_id}` | Path ID | Aggregate progress | `USER_PROGRESS_NOT_FOUND` | 4 — pending |
| `GET` | `/progress/{user_id}/knowledge-units/{unit_id}` | Path IDs | Unit mastery detail | `MASTERY_NOT_FOUND` | 4 — pending |
| `POST` | `/learning-sessions/{session_id}/agent/run` | Trigger/request context | Agent run result | `AGENT_DISABLED`, `AGENT_NOT_ELIGIBLE` | 5 — pending |
| `GET` | `/learning-sessions/{session_id}/agent/traces` | Path ID | Redacted trace list | `SESSION_NOT_FOUND` | 5 — pending |

## Health endpoint

### `GET /health`

No authentication, request body, or external provider call is made by this
endpoint. The backend still validates required `.env` values at process startup,
including `LLM_API_KEY`, `LLM_BASE_URL`, and `LLM_MODEL`; `/health` itself never
sends them to a provider or exposes them in its response.

Expected HTTP `200` shape:

```json
{
  "status": "ok",
  "app_name": "Adaptive Learning System",
  "environment": "development",
  "database": "configured"
}
```

- `status` is the backend liveness state.
- `app_name` and `environment` come from validated settings.
- `database` is a non-sensitive readiness/configuration indicator; it must not expose the database URL or local file path.

If a future readiness check determines the backend cannot serve requests, return HTTP `503` with the standard error envelope. The Phase 1 contract permits the non-sensitive value `configured`; later hardening may use another documented readiness value without adding secrets.

```bash
curl --fail http://127.0.0.1:8000/health
```

PowerShell:

```powershell
Invoke-RestMethod -Method Get -Uri http://127.0.0.1:8000/health
```

## Representative later-phase requests

Upload a PDF (Phase 2):

```bash
curl -X POST http://127.0.0.1:8000/documents/upload \
  -H "accept: application/json" \
  -F "file=@sample.pdf;type=application/pdf"
```

Create a learning session (Phase 4):

```bash
curl -X POST http://127.0.0.1:8000/learning-sessions \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":\"local-user\",\"document_id\":\"DOC_001\",\"knowledge_unit_id\":\"KU_001\"}"
```

Submit an answer (Phases 3–4):

```bash
curl -X POST http://127.0.0.1:8000/learning-sessions/SESSION_001/answers \
  -H "Content-Type: application/json" \
  -d "{\"question_id\":\"Q_001\",\"user_answer\":\"The validation gap suggests overfitting.\"}"
```

Run the agent (Phase 5):

```bash
curl -X POST http://127.0.0.1:8000/learning-sessions/SESSION_001/agent/run \
  -H "Content-Type: application/json" \
  -d "{\"reason\":\"REQUEST_DIFFERENT_EXPLANATION\"}"
```

These examples are design examples until their target phases are implemented.

## Standard error envelope

Later-phase endpoints should use:

```json
{
  "error": {
    "code": "DOCUMENT_NOT_FOUND",
    "message": "The requested document does not exist.",
    "details": {},
    "request_id": null
  }
}
```

Recommended status mapping:

| HTTP status | Use |
| --- | --- |
| `400` | Invalid content or state-independent input |
| `404` | Resource does not exist |
| `409` | State conflict, feature disabled, or transition not allowed |
| `413` | Upload exceeds configured size |
| `422` | Request/schema validation failure |
| `502` | Provider returned unusable output after bounded retries |
| `503` | Required dependency unavailable |
| `504` | LLM/provider timeout |

Error messages must be actionable and must never include API keys, provider authorization headers, full document content, or private agent reasoning.
