# Rule Engine

> **Delivery status:** Rule definitions are baselined in Phase 1. Their implementations and unit tests are scheduled across Phases 2–5 and remain pending.

Rules are deterministic code. Each result includes the rule ID, input summary, action, and human-readable reason. LLM output can provide semantic measurements or proposals but cannot bypass these rules.

## Knowledge Unit rules

| Rule ID | Input | Condition | Action | Reason | Test |
| --- | --- | --- | --- | --- | --- |
| KU-SPLIT-001 | `learning_objective_count` | `> KU_MAX_LEARNING_OBJECTIVES` | `SPLIT` | Unit tests too many outcomes | `test_split_when_too_many_objectives` |
| KU-SPLIT-002 | `key_concept_count` | `> KU_MAX_CONCEPTS` | `SPLIT` | Unit is conceptually too broad | `test_split_when_too_many_concepts` |
| KU-SPLIT-003 | `estimated_reading_minutes` | `> KU_MAX_READING_MINUTES` | `SPLIT` | Unit exceeds reading-time boundary | `test_split_when_too_long` |
| KU-MERGE-001 | concept count, objective independence | `< KU_MIN_CONCEPTS` and no independent objective | `MERGE` | Fragment has insufficient learning value | `test_merge_small_unit_without_objective` |
| KU-MERGE-002 | reading time, segment kind | `< KU_MIN_READING_MINUTES` and only an example | `MERGE` | Example should remain with its concept | `test_merge_short_example` |
| KU-MERGE-003 | question feasibility | Cannot generate an independent question | `MERGE` | Unit is not independently assessable | `test_merge_unassessable_unit` |
| KU-MERGE-004 | adjacent-topic similarity, objective overlap | Both classified high | `MERGE` | Adjacent units are materially redundant | `test_merge_overlapping_adjacent_units` |
| KU-LIMIT-001 | `refinement_round` | `>= KU_MAX_REFINEMENT_ROUNDS` | `STOP_INVALID` | Prevent unbounded split/merge loops | `test_refinement_stops_at_limit` |

## Question-selection rules

| Rule ID | Input | Condition | Action | Reason | Test |
| --- | --- | --- | --- | --- | --- |
| QS-001 | answer history | No history for unit | `RECALL` | Establish retrieval baseline | `test_first_question_is_recall` |
| QS-002 | `latest_recall_score` | `< 0.40` | `SCAFFOLDED_RECALL` | Recall needs support before abstraction | `test_low_recall_gets_scaffold` |
| QS-003 | `latest_score` | `0.40 <= score < 0.70` | `EXPLAIN` | Probe conceptual understanding | `test_mid_score_gets_explain` |
| QS-004 | `latest_score` | `>= 0.70` | `APPLY` | Seek application evidence | `test_high_score_gets_apply` |
| QS-005 | recall/application scores | recall `>= 0.75` and application `< 0.60` | `APPLICATION_DIAGNOSIS` | Diagnose recall–application gap | `test_recall_application_gap` |
| QS-006 | misconception history | Same misconception count `>= 2` | `ACTIVATE_TUTOR_AGENT` | Normal questioning is repeating failure | `test_repeated_misconception_requests_agent` |
| QS-007 | main question count | `>= MAX_MAIN_QUESTIONS_PER_UNIT` | `FINISH_OR_REMEDIATE` | Bound the main-question loop | `test_main_question_cap` |
| QS-008 | generated candidate/history | Material duplicate found | `REJECT_DUPLICATE` | Repetition supplies weak evidence | `test_duplicate_question_rejected` |

## Understanding and mastery rules

| Rule ID | Input | Condition | Action | Reason | Test |
| --- | --- | --- | --- | --- | --- |
| EV-STATE-001 | `overall_score` | `< 0.40` | `NOT_UNDERSTOOD` | Very low evidence | `test_not_understood_band` |
| EV-STATE-002 | `overall_score` | `0.40 <= score < 0.60` | `PARTIAL_RECALL` | Some retrieval, insufficient coverage | `test_partial_recall_band` |
| EV-STATE-003 | `overall_score` | `0.60 <= score < 0.75` | `BASIC_UNDERSTANDING` | Basic but incomplete evidence | `test_basic_understanding_band` |
| EV-STATE-004 | `overall_score` | `0.75 <= score < 0.90` | `GOOD_UNDERSTANDING` | Strong non-terminal answer | `test_good_understanding_band` |
| EV-STATE-005 | `overall_score` | `>= 0.90` | `STRONG_ANSWER` | Excellent latest-answer evidence | `test_strong_answer_band` |
| MS-UPDATE-001 | old mastery, answer score, difficulty | Accepted schema-valid evaluation | `UPDATE_AND_CLAMP` | Weighted evidence update | `test_mastery_formula_and_clamp` |
| MS-EVIDENCE-001 | equivalent attempt number | 1st/2nd/3rd+ | weight `1.0/0.5/0.25` | Repeated prompts are less independent | `test_repeated_evidence_weights` |
| MS-MASTERED-001 | mastery, evidence, application, misconceptions | All mastery predicates true | `MASTERED` | Require stable, applied evidence | `test_mastered_requires_all_predicates` |
| MS-MASTERED-002 | any one answer | Evidence count `< MIN_QUESTIONS_FOR_MASTERY` | `NOT_MASTERED` | Never master from one answer | `test_one_answer_never_mastered` |
| EV-CONFIDENCE-001 | evaluator confidence | Below configured policy threshold | `ASK_CLARIFICATION` | Avoid unsupported severe diagnosis | `test_low_confidence_asks_clarification` |

## Agent-trigger rules

| Rule ID | Input | Condition | Action | Reason | Test |
| --- | --- | --- | --- | --- | --- |
| AG-001 | `AGENT_ENABLED` | `false` | `NEVER_ACTIVATE` | Configuration is an absolute gate | `test_disabled_agent_never_runs` |
| AG-002 | misconception count | `>= AGENT_TRIGGER_WRONG_COUNT` | `ACTIVATE` | Misconception is recurring | `test_agent_trigger_wrong_count` |
| AG-003 | latest score, remediation attempts | score `< AGENT_TRIGGER_LOW_SCORE` and attempts `>= 2` | `ACTIVATE` | Bounded remediation did not help | `test_agent_trigger_after_failed_remediation` |
| AG-004 | recall/application scores | difference `>= AGENT_TRIGGER_RECALL_APPLICATION_GAP` | `ACTIVATE` | Needs adaptive application support | `test_agent_trigger_score_gap` |
| AG-005 | current agent step | `>= AGENT_MAX_STEPS` | `STOP_MAX_STEPS` | Agent execution must be bounded | `test_agent_stops_at_max_steps` |

## Priority and conflict resolution

Rules are evaluated in this order:

1. input validity and hard safety gates;
2. disabled feature and maximum-count gates;
3. repeated-misconception or failed-remediation triggers;
4. recall–application diagnosis;
5. no-history rule; and
6. mutually exclusive score bands.

An earlier terminal action wins. Every triggered rule is recorded for diagnostics, but only the winning action changes state. Threshold boundaries use the exact inclusive/exclusive operators shown above.

## Implementation contract

- Keep rule functions free of database and network side effects.
- Pass typed input snapshots and return typed decisions.
- Read tunable thresholds from validated settings.
- Unit-test both sides of every threshold, including exact boundary values.
- Update this table and `DECISIONS.md` before changing policy semantics.

