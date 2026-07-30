# API Specification

> **Delivery status:** Health, document upload/processing/read, Knowledge Map,
> and Knowledge Unit read endpoints were implemented through Phase 2. Learning,
> progress, question, and agent endpoints are implemented through Phase 5.

Base URL for local development: `http://127.0.0.1:8000`.

## Endpoint inventory

| Method | Path | Request | Success response | Common errors | Phase/status |
| --- | --- | --- | --- | --- | --- |
| `GET` | `/health` | None | Health object | `503 SERVICE_UNAVAILABLE` | 1 — completed |
| `POST` | `/documents/upload` | Multipart PDF | `Document` | `INVALID_FILE_TYPE`, `FILE_TOO_LARGE` | 2 — completed |
| `POST` | `/documents/{document_id}/process` | Empty | Processing result | `DOCUMENT_NOT_FOUND`, `PDF_TEXT_UNAVAILABLE` | 2 — completed |
| `GET` | `/documents` | `status`, `offset`, `limit` | Direct Document list | `DATABASE_ERROR` | 2 — completed |
| `GET` | `/documents/{document_id}` | Path ID | `Document` | `DOCUMENT_NOT_FOUND` | 2 — completed |
| `GET` | `/documents/{document_id}/knowledge-map` | Path ID | Knowledge Map object | `KNOWLEDGE_MAP_NOT_READY` | 2 — completed |
| `GET` | `/knowledge-units/{unit_id}` | Path ID | `KnowledgeUnit` | `KNOWLEDGE_UNIT_NOT_FOUND` | 2 — completed |
| `GET` | `/knowledge-units/{unit_id}/questions` | Path ID | Question summaries | `UNIT_NOT_FOUND` | 3 — complete |
| `POST` | `/knowledge-units/{unit_id}/generate-questions` | None | Accepted questions | `NO_VALID_QUESTION`, `LLM_UNAVAILABLE` | 3 — complete |
| `POST` | `/learning-sessions` | user/document/unit selection | `LearningSession` | `DOCUMENT_NOT_READY` | 4 — complete |
| `GET` | `/learning-sessions/{session_id}` | Path ID | Session state | `SESSION_NOT_FOUND` | 4 — complete |
| `GET` | `/learning-sessions/{session_id}/next-question` | Path ID | Next activity | `NO_NEXT_ACTIVITY` | 4 — complete |
| `POST` | `/learning-sessions/{session_id}/answers` | question ID and answer | Evaluation/mastery | `INVALID_ANSWER`, `EVALUATION_FAILED` | 3–4 — complete |
| `POST` | `/learning-sessions/{session_id}/finish-unit` | None | Updated session | `UNIT_NOT_FINISHABLE` | 4 — complete |
| `GET` | `/progress/{user_id}` | Path ID | Aggregate progress | — | 4 — complete |
| `GET` | `/progress/{user_id}/knowledge-units/{unit_id}` | Path IDs | Unit mastery detail | `MASTERY_NOT_FOUND` | 4 — complete |
| `POST` | `/learning-sessions/{session_id}/agent/run` | Trigger/request context | Agent run result | `AGENT_DISABLED`, `AGENT_NOT_ELIGIBLE` | 5 — complete |
| `GET` | `/learning-sessions/{session_id}/agent/traces` | Path ID | Redacted trace list | `SESSION_NOT_FOUND` | 5 — complete |

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

## Phase 2 document processing

Upload a PDF:

```bash
curl -X POST http://127.0.0.1:8000/documents/upload \
  -H "accept: application/json" \
  -F "file=@sample.pdf;type=application/pdf"
```

Success is HTTP `201` with a direct public Document object. The internal
`file_path` is never returned.

Process the uploaded document:

```bash
curl -X POST http://127.0.0.1:8000/documents/DOCUMENT_ID/process
```

The synchronous HTTP `200` response contains:

```json
{
  "document": {
    "id": "DOCUMENT_ID",
    "filename": "sample.pdf",
    "page_count": 3,
    "status": "ready",
    "created_at": "2026-07-30T08:00:00Z",
    "processed_at": "2026-07-30T08:00:05Z"
  },
  "knowledge_units": [
    {
      "id": "UNIT_ID",
      "document_id": "DOCUMENT_ID",
      "position": 1,
      "title": "Generalization and Data Splits",
      "summary": "A concise source-grounded summary.",
      "learning_objectives": ["Explain held-out evaluation"],
      "key_concepts": ["generalization", "validation set"],
      "concept_relations": [],
      "prerequisites": [],
      "common_misconceptions": [],
      "source_pages": [1],
      "estimated_reading_minutes": 3,
      "status": "valid"
    }
  ],
  "coverage": {
    "readable_pages": 3,
    "covered_pages": 3,
    "coverage_ratio": 1.0
  }
}
```

Read persisted results:

```bash
curl http://127.0.0.1:8000/documents
curl http://127.0.0.1:8000/documents/DOCUMENT_ID
curl http://127.0.0.1:8000/documents/DOCUMENT_ID/knowledge-map
curl http://127.0.0.1:8000/knowledge-units/UNIT_ID
```

Upload/processing codes include `EMPTY_FILE`, `INVALID_FILE_TYPE`,
`INVALID_PDF_SIGNATURE`, `FILE_TOO_LARGE`, `PDF_ENCRYPTED`, `PDF_EMPTY`,
`PDF_UNREADABLE`, `PDF_TEXT_UNAVAILABLE`, `LLM_TIMEOUT`,
`LLM_INVALID_OUTPUT`, `LLM_PROVIDER_ERROR`, `INVALID_SOURCE_COVERAGE`, and
`NO_VALID_KNOWLEDGE_UNITS`.

Learning-session, answer, progress, question, and agent calls use the same
stable error envelope and do not expose stored reference answers or rubrics.

## Standard error envelope

Implemented application errors use:

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
