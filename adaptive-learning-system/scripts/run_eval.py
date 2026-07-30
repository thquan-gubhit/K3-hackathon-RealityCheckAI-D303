import json
import logging
from pathlib import Path

from app.config import get_settings
from app.llm.adapter import LLMClient
from app.llm.prompts import build_answer_evaluation_messages
from app.schemas.evaluation import AnswerEvaluation
from app.schemas.question import QuestionRubric

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GOLDEN_SET_PATH = PROJECT_ROOT / "eval" / "golden_set.json"

def run_evaluation() -> None:
    if not GOLDEN_SET_PATH.exists():
        logger.error(f"Golden set not found at {GOLDEN_SET_PATH}")
        return

    with open(GOLDEN_SET_PATH, "r", encoding="utf-8") as f:
        cases = json.load(f)

    settings = get_settings()
    llm_client = LLMClient(settings)
    
    total = len(cases)
    passed = 0
    failed_cases = []

    for i, case in enumerate(cases):
        logger.info(f"Running TC-{i+1:03d} / {total}: {case['scenario_type']} - {case['topic']}")
        
        rubric_lines = [line.strip("- ") for line in case["rubric"].split("\n") if line.strip()]
        weight_per_point = 1.0 / len(rubric_lines) if rubric_lines else 1.0
        rubric_points = [{"point": line, "weight": weight_per_point} for line in rubric_lines]
        
        # Adjust sum to exactly 1.0 to satisfy Pydantic validator
        rubric_weight_total = sum(rp["weight"] for rp in rubric_points)
        if abs(rubric_weight_total - 1.0) > 1e-6 and rubric_points:
            rubric_points[-1]["weight"] += (1.0 - rubric_weight_total)

        rubric = QuestionRubric(
            required_points=rubric_points,
            optional_points=[],
            acceptable_alternatives=[],
            misconceptions=[],
            dimension_weights={"correctness": 0.4, "coverage": 0.3, "reasoning": 0.2, "application": 0.1}
        )

        messages = build_answer_evaluation_messages(
            question_id=f"q_{i}",
            question_text=case["question"],
            reference_answer="Reference derived from rubric.",
            rubric=rubric,
            source_context=case["topic"], # Fake source context just to pass validation
            user_answer=case["learner_answer"],
        )

        try:
            evaluation = llm_client.generate_structured(messages, AnswerEvaluation)
            
            # Check correctness
            corr_min, corr_max = case["expected_correctness_score"]
            actual_corr = evaluation.dimension_scores.correctness
            corr_pass = corr_min <= actual_corr <= corr_max

            # Check coverage
            cov_min, cov_max = case["expected_coverage_score"]
            actual_cov = evaluation.dimension_scores.coverage
            cov_pass = cov_min <= actual_cov <= cov_max

            # Check misconception
            has_misc = len(evaluation.detected_misconceptions) > 0
            misc_pass = has_misc == case["expected_has_misconception"]
            
            if corr_pass and cov_pass and misc_pass:
                passed += 1
                logger.info(" -> PASS")
            else:
                logger.warning(f" -> FAIL")
                logger.warning(f"    Expected Corr: [{corr_min}, {corr_max}], Actual: {actual_corr}")
                logger.warning(f"    Expected Cov: [{cov_min}, {cov_max}], Actual: {actual_cov}")
                logger.warning(f"    Expected Misc: {case['expected_has_misconception']}, Actual: {has_misc} ({evaluation.detected_misconceptions})")
                logger.warning(f"    Feedback: {evaluation.feedback}")
                failed_cases.append(case['id'])
                
        except Exception as e:
            logger.error(f" -> ERROR: {e}")

    accuracy = passed / total if total > 0 else 0
    logger.info("========================================")
    logger.info(f"EVALUATION RESULT: {passed}/{total} passed ({accuracy*100:.2f}%)")
    if accuracy >= 0.90:
        logger.info("QUALITY BAR MET! (\u2265 90%)")
    else:
        logger.warning(f"FAILED QUALITY BAR (< 90%). Failed cases: {failed_cases}")
    logger.info("========================================")

if __name__ == "__main__":
    run_evaluation()
