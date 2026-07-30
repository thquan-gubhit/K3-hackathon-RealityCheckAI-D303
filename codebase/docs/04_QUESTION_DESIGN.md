# Question Design

> **Delivery status:** Implemented and verified in Phase 3. Recall, Explain, and
> Apply questions pass deterministic validation and are stored with their
> pre-answer reference/rubric before public exposure.

## Question types

| Type | Purpose | Typical evidence |
| --- | --- | --- |
| `RECALL` | Retrieve a fact, definition, or relationship without cues | Correct core idea from memory |
| `SCAFFOLDED_RECALL` | Retry recall with a bounded cue | Recovery after low recall |
| `EXPLAIN` | Express mechanism or causal relationship in the learner's own words | Reasoning and conceptual links |
| `RELATE` | Connect two concepts from the source | Accurate relationship and direction |
| `APPLY` | Use the concept in a source-grounded scenario | Correct diagnosis or decision |
| `MISCONCEPTION` | Distinguish a tempting false belief from the source | Explicit correction and justification |
| `TRANSFER` | Apply an established idea in a novel but supportable setting | Generalization without outside facts |

Recall, Explain, and Apply are mandatory for the MVP. The remaining types support routing and remediation.

## Question lifecycle

1. Select a Knowledge Unit and one learning objective.
2. Use deterministic rules to select the question type and difficulty.
3. Generate several source-grounded candidates.
4. Generate a reference answer and rubric **before** showing the question.
5. Validate each candidate.
6. Reject ambiguous, answer-leaking, external-knowledge, unsupported, or duplicate candidates.
7. Persist the accepted question, reference answer, rubric, and source pages together.
8. Never mutate the rubric in response to the learner's answer.

## Quality criteria

An accepted question:

- is answerable from the supplied source context;
- tests exactly the selected objective;
- has one clear task and appropriate cognitive level;
- does not reveal the answer in its wording;
- does not require facts outside the document;
- includes enough context to avoid ambiguity;
- is not materially equivalent to a recent question;
- has a reference answer and weighted rubric whose required-point weights are coherent; and
- carries source-page provenance.

## Target question schema

```json
{
  "id": "Q_001",
  "knowledge_unit_id": "KU_001",
  "learning_objective": "Recognize evidence of overfitting",
  "question_type": "apply",
  "difficulty": "medium",
  "question_text": "A model has 99% training accuracy and 70% validation accuracy. What is likely happening, and why?",
  "reference_answer": "The large train-validation gap suggests overfitting and weak generalization.",
  "rubric": {
    "required_points": [
      {"point": "Identifies overfitting", "weight": 0.35},
      {"point": "Uses the train-validation gap as evidence", "weight": 0.30},
      {"point": "Explains weak generalization", "weight": 0.25}
    ],
    "optional_points": [
      {"point": "Names a source-supported mitigation", "weight": 0.10}
    ],
    "acceptable_alternatives": ["regularization", "early stopping"],
    "misconceptions": ["Training accuracy alone proves model quality"],
    "dimension_weights": {
      "correctness": 0.35,
      "coverage": 0.25,
      "reasoning": 0.25,
      "application": 0.15
    }
  },
  "source_pages": [5, 6],
  "validation_status": "accepted"
}
```

## Rubric design

- Required points state the minimum evidence for a strong answer.
- Optional points reward additional source-grounded value without making it mandatory.
- Acceptable alternatives prevent brittle wording matches.
- Misconceptions are explicit claims to detect, not merely missing points.
- Dimension weights sum to `1.0`; point weights are normalized or rejected.
- The evaluator receives only the stored question, source context, reference answer, rubric, and learner answer.
- A response with insufficient source evidence returns an `INSUFFICIENT_CONTEXT` outcome instead of inventing a grade.

## Validation failure reasons

Use stable reasons such as `NOT_SOURCE_GROUNDED`, `OBJECTIVE_MISMATCH`, `ANSWER_LEAK`, `AMBIGUOUS`, `EXTERNAL_KNOWLEDGE_REQUIRED`, `DUPLICATE`, and `INVALID_RUBRIC`. Rejected candidates are not shown to the learner.
