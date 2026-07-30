"""Language-consistency requirements embedded in every learner-facing prompt."""

from app.llm.prompts import (
    ANSWER_EVALUATION_PROMPT_V1,
    KNOWLEDGE_UNIT_SYSTEM_PROMPT,
    QUESTION_GENERATION_PROMPT_V1,
    SOURCE_LANGUAGE_POLICY,
    TUTOR_AGENT_SYSTEM_PROMPT_V1,
)


def test_shared_policy_makes_slide_language_authoritative() -> None:
    normalized = " ".join(SOURCE_LANGUAGE_POLICY.split())
    assert "dominant natural language" in normalized
    assert "authoritative output language" in normalized
    assert "Do not default to English" in normalized
    assert "Never translate JSON" in normalized


def test_knowledge_units_use_the_authoritative_source_language() -> None:
    assert SOURCE_LANGUAGE_POLICY in KNOWLEDGE_UNIT_SYSTEM_PROMPT
    assert "candidate title, summary, learning objective" in (
        KNOWLEDGE_UNIT_SYSTEM_PROMPT
    )


def test_questions_and_rubrics_use_source_context_language() -> None:
    assert SOURCE_LANGUAGE_POLICY in QUESTION_GENERATION_PROMPT_V1
    assert "Infer the authoritative language from source_context" in (
        QUESTION_GENERATION_PROMPT_V1
    )
    assert "question_text" in QUESTION_GENERATION_PROMPT_V1
    assert "reference_answer" in QUESTION_GENERATION_PROMPT_V1
    assert "rubric point" in QUESTION_GENERATION_PROMPT_V1


def test_evaluation_feedback_does_not_follow_answer_language() -> None:
    assert SOURCE_LANGUAGE_POLICY in ANSWER_EVALUATION_PROMPT_V1
    assert "even when the learner answers in another language" in (
        ANSWER_EVALUATION_PROMPT_V1
    )
    assert "feedback" in ANSWER_EVALUATION_PROMPT_V1


def test_tutor_keeps_schema_values_while_using_source_language() -> None:
    assert SOURCE_LANGUAGE_POLICY in TUTOR_AGENT_SYSTEM_PROMPT_V1
    assert "Keep action" in TUTOR_AGENT_SYSTEM_PROMPT_V1
    assert "schema-controlled values unchanged" in TUTOR_AGENT_SYSTEM_PROMPT_V1
