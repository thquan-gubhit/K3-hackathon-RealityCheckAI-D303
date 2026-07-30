# Data Model

> **Delivery status:** Phase 1 provides the SQLite/SQLAlchemy foundation. The domain entities below are the target model for Phases 2–5 and are not claimed to exist in Phase 1.

## Entity outline

| Entity | Core fields | Relationships | Target phase |
| --- | --- | --- | --- |
| `Document` | `id`, `filename`, `file_path`, `page_count`, `status`, `created_at`, `processed_at` | Has many pages, units, and sessions | 2 |
| `DocumentPage` | `id`, `document_id`, `page_number`, `raw_text`, `cleaned_text`, `heading` | Belongs to document | 2 |
| `KnowledgeUnit` | `id`, `document_id`, `title`, `summary`, JSON metadata, reading time, `status` | Belongs to document; has many questions | 2 |
| `Question` | `id`, `knowledge_unit_id`, type, difficulty, text, answer, rubric/source JSON, status, `created_at` | Belongs to KU; has many attempts | 3 |
| `LearningSession` | `id`, `user_id`, `document_id`, timestamps, `status` | Belongs to document/user; has attempts/traces | 4 |
| `AnswerAttempt` | `id`, `session_id`, `question_id`, answer, evaluation JSON, score, attempt, `created_at` | Belongs to session and question | 3–4 |
| `MasteryState` | `id`, `user_id`, `knowledge_unit_id`, dimension scores, mastery, status, evidence count, `last_updated` | One logical row per user/KU | 4 |
| `Misconception` | `id`, `user_id`, `knowledge_unit_id`, concept, description, count, severity, resolved, detection time | Belongs to user/KU | 4 |
| `AgentTrace` | `id`, `session_id`, `knowledge_unit_id`, trigger, step, action, arguments/observation JSON, status, `created_at` | Belongs to session/KU | 5 |

The MVP may use a stable local default `user_id`; a complete account system is outside scope.

## Entity-relationship diagram

```mermaid
erDiagram
    DOCUMENT ||--o{ DOCUMENT_PAGE : contains
    DOCUMENT ||--o{ KNOWLEDGE_UNIT : organizes
    DOCUMENT ||--o{ LEARNING_SESSION : studied_in
    KNOWLEDGE_UNIT ||--o{ QUESTION : assessed_by
    LEARNING_SESSION ||--o{ ANSWER_ATTEMPT : records
    QUESTION ||--o{ ANSWER_ATTEMPT : answered_as
    KNOWLEDGE_UNIT ||--o{ MASTERY_STATE : measured_by
    KNOWLEDGE_UNIT ||--o{ MISCONCEPTION : has_evidence
    LEARNING_SESSION ||--o{ AGENT_TRACE : emits
    KNOWLEDGE_UNIT ||--o{ AGENT_TRACE : concerns

    DOCUMENT {
        string id PK
        string filename
        string file_path
        int page_count
        string status
        datetime created_at
        datetime processed_at
    }
    DOCUMENT_PAGE {
        string id PK
        string document_id FK
        int page_number
        text raw_text
        text cleaned_text
        string heading
    }
    KNOWLEDGE_UNIT {
        string id PK
        string document_id FK
        string title
        text summary
        text learning_objectives_json
        text key_concepts_json
        text concept_relations_json
        text prerequisites_json
        text misconceptions_json
        text source_pages_json
        int estimated_reading_minutes
        string status
    }
    QUESTION {
        string id PK
        string knowledge_unit_id FK
        string question_type
        string difficulty
        text question_text
        text reference_answer
        text rubric_json
        text source_pages_json
        string validation_status
        datetime created_at
    }
    LEARNING_SESSION {
        string id PK
        string user_id
        string document_id FK
        datetime started_at
        datetime completed_at
        string status
    }
    ANSWER_ATTEMPT {
        string id PK
        string session_id FK
        string question_id FK
        text user_answer
        text evaluation_json
        float overall_score
        int attempt_number
        datetime created_at
    }
    MASTERY_STATE {
        string id PK
        string user_id
        string knowledge_unit_id FK
        float recall_score
        float understanding_score
        float application_score
        float mastery_score
        string status
        int question_evidence_count
        datetime last_updated
    }
    MISCONCEPTION {
        string id PK
        string user_id
        string knowledge_unit_id FK
        string concept
        text description
        int occurrence_count
        string severity
        bool resolved
        datetime last_detected_at
    }
    AGENT_TRACE {
        string id PK
        string session_id FK
        string knowledge_unit_id FK
        string trigger_reason
        int step_number
        string action
        text arguments_json
        text observation_json
        string status
        datetime created_at
    }
```

## JSON fields

| Field | Expected shape | Validation |
| --- | --- | --- |
| `learning_objectives_json` | array of 1–3 strings | Non-empty, deduplicated |
| `key_concepts_json` | array of 2–7 strings | Non-empty, deduplicated |
| `concept_relations_json` | array of `{source, relation, target}` | All keys required |
| `prerequisites_json` | array of KU identifiers | Known identifiers; no self-reference |
| `misconceptions_json` | array of strings | Non-empty entries |
| `source_pages_json` | sorted array of positive integers | Pages belong to document |
| `rubric_json` | required/optional points, alternatives, misconceptions, dimensions | Pydantic-valid; weights coherent |
| `evaluation_json` | scores, evidence lists, feedback, action, confidence | Scores in `[0,1]` |
| `arguments_json` | action-specific object | Matches registered tool schema |
| `observation_json` | redacted tool result/status | No secrets or private reasoning |

SQLite stores these as JSON-serialized text unless SQLAlchemy's JSON abstraction is used. Pydantic domain schemas remain the source of shape validation.

## Constraints and indexes

| Table | Constraint/index | Purpose |
| --- | --- | --- |
| `document_pages` | unique `(document_id, page_number)` | Prevent duplicate page ingestion |
| `knowledge_units` | index `(document_id, status)` | Load a valid Knowledge Map |
| `questions` | index `(knowledge_unit_id, question_type, validation_status)` | Select eligible questions |
| `learning_sessions` | index `(user_id, status, started_at)` | Resume recent session |
| `answer_attempts` | unique `(session_id, question_id, attempt_number)` | Stable attempt ordering |
| `answer_attempts` | index `(session_id, created_at)` | Load history |
| `mastery_states` | unique `(user_id, knowledge_unit_id)` | One current state per user/KU |
| `misconceptions` | index `(user_id, knowledge_unit_id, resolved)` | Find active misconceptions |
| `agent_traces` | unique `(session_id, step_number)` | Enforce ordered bounded steps |

Foreign keys should be enabled for SQLite connections. Destructive cascade behavior must be chosen explicitly in a later migration decision; it is not assumed by this skeleton.

