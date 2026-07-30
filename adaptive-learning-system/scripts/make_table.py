import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GOLDEN_SET_PATH = PROJECT_ROOT / "eval" / "golden_set.json"
OUTPUT_PATH = PROJECT_ROOT / "docs" / "07_GOLDEN_SET.md"

def generate():
    with open(GOLDEN_SET_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    lines = []
    lines.append('# Chi tiết 20 Test Cases (Golden Set)\n')
    lines.append('Dưới đây là chi tiết 20 kịch bản kiểm thử được sử dụng để đánh giá năng lực chấm điểm của AI Evaluator.\n')
    lines.append('| ID | Loại (Scenario) | Chủ đề | Câu hỏi | Câu trả lời của học viên | Điểm kỳ vọng | Misconception |')
    lines.append('|---|---|---|---|---|---|---|')

    for item in data:
        qid = item['id']
        stype = item['scenario_type']
        topic = item['topic']
        q = item['question'].replace('\n', ' ')
        ans = item['learner_answer'].replace('\n', ' ')
        score = f"Corr: {item['expected_correctness_score']}<br>Cov: {item['expected_coverage_score']}"
        misc = "Có" if item['expected_has_misconception'] else "Không"
        lines.append(f"| **{qid}** | {stype} | {topic} | {q} | {ans} | {score} | {misc} |")

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"Generated {OUTPUT_PATH}")

if __name__ == "__main__":
    generate()
