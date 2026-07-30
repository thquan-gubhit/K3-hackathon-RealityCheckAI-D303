# Knowledge Unit Design

> **Delivery status:** Implemented and verified in Phase 2. Question generation
> remains Phase 3 work.

## Definition

A Knowledge Unit (KU) is a cohesive group of source-grounded ideas with one central topic, 1–3 learning objectives, 2–7 key concepts, and enough substance for at least one meaningful independent question. A valid unit should take approximately 2–10 minutes to read.

## Validity criteria

- One recognizable central topic.
- One to three observable learning objectives.
- Two to seven key concepts.
- Source pages are present and belong to the parent document.
- Concepts and objectives are supported by the source text.
- The unit can produce an independent question without relying on hidden context.
- Prerequisites and relations reference known concepts or unit identifiers.

## Too broad

A candidate must be considered for `SPLIT` when any of these applies:

- learning objectives exceed `KU_MAX_LEARNING_OBJECTIVES`;
- key concepts exceed `KU_MAX_CONCEPTS`;
- estimated reading time exceeds `KU_MAX_READING_MINUTES`;
- the title combines separable topics;
- a question cannot assess the unit without testing several unrelated skills.

Split boundaries should favor headings, topic changes, and coherent source-page ranges. Splitting must not silently drop source coverage.

## Too small

A candidate must be considered for `MERGE` when any of these applies:

- concepts are below `KU_MIN_CONCEPTS` and there is no independent objective;
- reading time is below `KU_MIN_READING_MINUTES` and the candidate is only an example;
- no meaningful independent question can be generated;
- the next unit is highly similar and its objectives overlap substantially.

Merge with the most coherent adjacent unit, then rerun all size and coverage checks.

## Split/merge policy

1. The LLM proposes candidate segments and semantic metadata.
2. Pydantic validates shape and value ranges.
3. deterministic rules return `ACCEPT`, `SPLIT`, or `MERGE` with a rule ID and reason;
4. at most `KU_MAX_REFINEMENT_ROUNDS` refinement rounds are allowed;
5. coverage and duplicate checks run over the final set; and
6. invalid output after the limit fails with a recoverable domain error rather than being saved as valid.

## Target schema

```json
{
  "id": "KU_001",
  "document_id": "DOC_001",
  "title": "Overfitting and Generalization",
  "summary": "How a model can fit training data while performing poorly on unseen data.",
  "learning_objectives": [
    "Explain overfitting",
    "Recognize evidence of overfitting",
    "Propose a suitable mitigation"
  ],
  "key_concepts": [
    "training error",
    "validation error",
    "generalization",
    "regularization"
  ],
  "concept_relations": [
    {
      "source": "training-validation gap",
      "relation": "indicates",
      "target": "overfitting"
    }
  ],
  "prerequisites": [],
  "common_misconceptions": [
    "High training accuracy always means the model is good"
  ],
  "source_pages": [5, 6, 7, 8],
  "estimated_reading_minutes": 6,
  "status": "valid"
}
```

## Example validation outcome

```json
{
  "unit_id": "KU_CANDIDATE_04",
  "action": "SPLIT",
  "triggered_rules": ["KU-SPLIT-002", "KU-SPLIT-003"],
  "reason": "The candidate has 10 concepts and an estimated reading time of 14 minutes.",
  "suggested_boundary": "Separate diagnosis from mitigation techniques."
}
```

## Coverage invariants

- Every final KU has at least one source page.
- Important readable pages are represented by at least one KU or explicitly recorded as excluded with a reason.
- Serious duplicate units are rejected.
- Source page order is normalized and duplicates are removed.
- Refinement never exceeds its configured round limit.

## Phase 2 implementation

- `KnowledgeUnitBatch` and every candidate are validated by Pydantic before
  deterministic rules inspect them.
- Candidate IDs are temporary LLM-local references. Persistence assigns UUIDs
  and translates prerequisite references to the final UUIDs.
- Headings are the primary deterministic segment boundary; pages without a
  heading stay with the preceding topic until the 1,200-word ceiling.
- Blank pages are retained as explicit exclusions with a reason.
- Final persistence accepts only 3–10 units with complete source coverage, no
  serious duplicates, contiguous positions, and `valid` status.
- Split/merge calls must preserve the exact union of their input source pages.
