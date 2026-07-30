# Evaluation and Mastery

> **Delivery status:** Formulas and schemas are baselined in Phase 1. Answer evaluation is Phase 3 and mastery/adaptive updates are Phase 4; neither is implemented as part of Phase 1.

## Evaluation dimensions

| Dimension | Meaning | Example signal |
| --- | --- | --- |
| Correctness | Claims agree with the source and reference answer | No factual contradiction |
| Coverage | Required rubric points are present | Core evidence is not omitted |
| Reasoning | Relationships or mechanisms are explained | Cause and consequence are connected |
| Application | The concept is used appropriately in a scenario | Correct diagnosis or action |

All dimension scores, `overall_score`, and `confidence` must be within `[0, 1]`.

## Structured evaluation contract

```json
{
  "overall_score": 0.72,
  "dimension_scores": {
    "correctness": 0.9,
    "coverage": 0.7,
    "reasoning": 0.6,
    "application": 0.7
  },
  "correct_points": ["Correctly identifies overfitting"],
  "missing_points": ["Does not explain weak generalization"],
  "incorrect_points": [],
  "contradictions": [],
  "detected_misconceptions": [],
  "feedback": "You identified the pattern; connect the validation gap to generalization.",
  "recommended_next_action": "ASK_EXPLAIN_QUESTION",
  "confidence": 0.86
}
```

The evaluator must use the rubric stored before the answer, cite only source-supported evidence, and return Pydantic-valid JSON.

## Understanding bands

| Overall score | State |
| --- | --- |
| `< 0.40` | `NOT_UNDERSTOOD` |
| `0.40–<0.60` | `PARTIAL_RECALL` |
| `0.60–<0.75` | `BASIC_UNDERSTANDING` |
| `0.75–<0.90` | `GOOD_UNDERSTANDING` |
| `≥ 0.90` | `STRONG_ANSWER` |

These states describe the latest answer; none alone implies `MASTERED`.

## Mastery formula

For each accepted answer:

```text
adjusted_score = answer_score × difficulty_multiplier

new_mastery =
    MASTERY_OLD_WEIGHT × old_mastery
    + MASTERY_NEW_WEIGHT × adjusted_score

new_mastery = clamp(new_mastery, 0, 1)
```

Only the final mastery value is clamped. In particular, a hard-question
multiplier may make `adjusted_score` greater than `1.0` before the weighted
update.

Default difficulty multipliers:

| Difficulty | Multiplier |
| --- | --- |
| Easy | `0.80` |
| Medium | `1.00` |
| Hard | `1.15` |

Repeated versions of materially the same question provide less independent evidence:

| Attempt on equivalent evidence | Evidence weight |
| --- | --- |
| First | `1.00` |
| Second | `0.50` |
| Third and later | `0.25` |

The evidence weight reduces that attempt's contribution when aggregating dimension evidence and counting independent questions; it must not allow repeated memorization to satisfy the independent-question condition.

## Recall versus understanding

- **Recall** measures retrieval of relevant facts or relationships.
- **Understanding** measures coverage plus explanation of how or why those ideas relate.
- A learner may recall terminology yet fail to explain a mechanism.
- Application is tracked separately so high recall cannot hide a recall–application gap.

## `MASTERED` condition

All conditions are required:

```text
mastery_score >= MASTERY_THRESHOLD
AND answered_independent_questions >= MIN_QUESTIONS_FOR_MASTERY
AND has_application_evidence = true
AND has_critical_misconception = false
```

No single answer can mark a unit `MASTERED`.

## Confidence handling

- Low evaluator confidence must not create a new critical misconception automatically.
- The next action becomes `ASK_CLARIFICATION` or manual review, according to policy.
- Invalid or out-of-range scores are rejected before persistence.
- Confidence is evaluation metadata; it is not multiplied directly into correctness unless a later ADR explicitly changes the formula.
- A conflicting high-severity finding should be preserved for review rather than silently overwritten.

## Update invariants

- Persist the answer, rubric identifier/version, evaluation, previous mastery, new mastery, and rule outcome atomically where practical.
- Clamp all calculated scores to `[0, 1]`.
- Ignore failed or schema-invalid evaluations for mastery updates.
- Recompute status only after the accepted attempt is stored.
