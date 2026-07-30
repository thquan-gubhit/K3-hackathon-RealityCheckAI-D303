# Workflows

> **Delivery status:** Document processing and Knowledge Unit generation are
> implemented in Phase 2. Question/evaluation and adaptive workflows were
> implemented and verified in Phases 3–4; Tutor Agent exceptions in Phase 5.

Workflows are explicit, bounded sequences. An API handler validates transport input and invokes a workflow; it does not call an LLM directly. Each LLM result must pass Pydantic and domain validation before persistence.

## Document processing

```mermaid
flowchart TD
    A[Upload PDF] --> B{File valid?}
    B -- No --> BX[Return stable file error]
    B -- Yes --> C[Store file metadata]
    C --> D[Parse text by page]
    D --> E{Readable text exists?}
    E -- No --> EX[Return PDF_TEXT_UNAVAILABLE]
    E -- Yes --> F[Detect headings and topic boundaries]
    F --> G[Create candidate segments]
    G --> H[Run Knowledge Unit generation workflow]
    H --> I[Validate coverage and duplicates]
    I --> J{Map valid?}
    J -- No --> JX[Fail with recoverable processing error]
    J -- Yes --> K[Save Knowledge Map]
```

Required postconditions:

- each saved page belongs to the document and keeps its page number;
- every Knowledge Unit has source pages;
- important readable pages are covered or explicitly excluded with a reason;
- no serious duplicate units are accepted; and
- retries and refinement rounds remain within configured limits.

## Knowledge Unit generation

```mermaid
flowchart TD
    A[Candidate segments] --> B[LLM extracts title, objectives, concepts, relations]
    B --> C{Pydantic schema valid?}
    C -- No and retries remain --> B
    C -- No retries left --> X[Fail: INVALID_LLM_OUTPUT]
    C -- Yes --> D[Rule Engine checks size and independence]
    D --> E{Decision}
    E -- ACCEPT --> F[Add valid candidate]
    E -- SPLIT --> G[Request bounded split refinement]
    E -- MERGE --> H[Merge with coherent adjacent candidate]
    G --> I{Refinement rounds remain?}
    H --> I
    I -- Yes --> D
    I -- No --> Y[Fail: NO_VALID_KNOWLEDGE_UNITS]
    F --> J[Validate total source coverage]
```

The LLM may propose a split or merge, but deterministic rules accept or reject that proposal.

## Question generation

```mermaid
flowchart TD
    A[Select Knowledge Unit] --> B[Select learning objective]
    B --> C[Rules select question type]
    C --> D[Generate bounded candidate set]
    D --> E[Generate reference answer]
    E --> F[Generate rubric before learner answer]
    F --> G{Question validator accepts?}
    G -- No; candidates remain --> H[Reject candidate with reason]
    H --> D
    G -- No candidates remain --> X[Fail: NO_VALID_QUESTION]
    G -- Yes --> I[Persist question, answer, rubric, provenance]
```

The validator checks source grounding, objective alignment, answer leakage, ambiguity, external knowledge, duplication, and rubric validity.

## Answer evaluation

```mermaid
flowchart TD
    A[Receive learner answer] --> B[Normalize input]
    B --> C[Load immutable question, rubric, and source context]
    C --> D[LLM evaluates against rubric]
    D --> E{Pydantic and score ranges valid?}
    E -- No and retries remain --> D
    E -- No retries left --> X[Fail without mastery update]
    E -- Yes --> F{Confidence sufficient?}
    F -- No --> G[Recommend ASK_CLARIFICATION]
    F -- Yes --> H[Classify evidence and misconceptions]
    G --> I[Persist answer attempt and evaluation]
    H --> I
    I --> J[Rules derive understanding state]
    J --> K[Phase 4: update mastery atomically]
```

The evaluator never changes the stored rubric. A failed evaluation is not evidence and must not update mastery.

## Adaptive learning

```mermaid
flowchart TD
    A[Load session, unit, history, mastery] --> B{No answer history?}
    B -- Yes --> C[Ask RECALL]
    B -- No --> D[Evaluate deterministic routing rules]
    D --> E{Question cap reached?}
    E -- Yes --> F[Finish unit or bounded remediation]
    E -- No --> G{Repeated misconception or remediation failure?}
    G -- No --> H[Choose scaffold, EXPLAIN, APPLY, or diagnosis]
    G -- Yes --> I{AGENT_ENABLED and trigger accepted?}
    I -- No --> J[Use deterministic remediation]
    I -- Yes --> K[Phase 5: run bounded Tutor Agent]
    C --> L[Present next activity]
    H --> L
    J --> L
    K --> L
    F --> M[Persist terminal/next-unit decision]
```

Routing priority is: safety/disabled checks, session limits, agent eligibility, application-gap diagnosis, then score-band selection.

## Cross-workflow guarantees

- Every transition produces a success result or a stable error code; errors are not swallowed.
- External calls have timeout and retry limits.
- Persisted terminal state is written only after its validation gates pass.
- Repeating a process request should not silently duplicate accepted domain records.
- Logs include operation, latency, model identifier, and status but exclude API keys and full document content at normal log levels.

## Implemented transaction boundaries

The synchronous Phase 2 workflow persists `processing` first, then commits
parsed pages so extraction evidence survives an LLM failure. A validated map
replacement and the `ready` transition commit together. Any known parse, LLM,
rule, or database failure rolls back current work and records `failed` when the
database remains available. Reprocessing replaces the existing map instead of
appending duplicate units.
