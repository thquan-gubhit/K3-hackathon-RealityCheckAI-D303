# Evaluation and Mastery

> **Delivery status:** Answer evaluation was implemented in Phase 3; mastery,
> evidence weighting, misconception tracking, and conservative mastery gates
> were implemented and verified in Phase 4.

## Evaluation dimensions

LLM evaluator trả về điểm trên 4 chiều đánh giá (mỗi chiều ∈ [0, 1]), mỗi chiều có cơ sở khoa học riêng:

| Dimension | Ý nghĩa | Cơ sở nghiên cứu | Ví dụ tín hiệu |
| --- | --- | --- | --- |
| **Correctness** | Các phát biểu đúng với tài liệu nguồn và đáp án mẫu | Roediger & Karpicke (2006), *Test-Enhanced Learning* | Không mâu thuẫn sự thật |
| **Coverage** | Các ý bắt buộc trong Rubric (Barem) đều có mặt | Mislevy & Haertel (2006), *Evidence-Centered Design* | Không bỏ sót ý trọng tâm |
| **Reasoning** | Giải thích được mối quan hệ, cơ chế, nguyên nhân–kết quả | Chi & Wylie (2014), *ICAP Framework* | Nguyên nhân và hệ quả được liên kết |
| **Application** | Áp dụng đúng khái niệm vào tình huống thực tế | Bransford & Schwartz (1999), *Rethinking Transfer* | Chẩn đoán hoặc hành động đúng |

Tất cả điểm chiều, `overall_score` và `confidence` bắt buộc nằm trong `[0, 1]`.

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

Evaluator bắt buộc phải sử dụng Rubric đã lưu trước khi người học trả lời, chỉ trích dẫn bằng chứng có trong tài liệu nguồn, và trả về JSON hợp lệ theo Pydantic schema.

## Understanding bands

| Overall score | State | Ý nghĩa |
| --- | --- | --- |
| `< 0.40` | `NOT_UNDERSTOOD` | Chưa hiểu |
| `0.40–<0.60` | `PARTIAL_RECALL` | Nhớ lại một phần |
| `0.60–<0.75` | `BASIC_UNDERSTANDING` | Hiểu cơ bản |
| `0.75–<0.90` | `GOOD_UNDERSTANDING` | Hiểu tốt |
| `≥ 0.90` | `STRONG_ANSWER` | Câu trả lời xuất sắc |

Các trạng thái này mô tả chất lượng câu trả lời mới nhất; không trạng thái nào đơn lẻ có thể ngụ ý `MASTERED`.

## Mastery formula (Exponential Moving Average)

Hệ thống sử dụng mô hình **Exponential Moving Average (EMA)** để cập nhật điểm mastery. EMA được chọn vì tính minh bạch (educator dễ hiểu), nhẹ nhàng (chạy real-time) và ưu tiên bài làm gần đây hơn (phản ánh trạng thái hiện tại của người học).

Với mỗi câu trả lời hợp lệ:

```text
adjusted_score = overall_score × difficulty_multiplier

effective_new_weight = MASTERY_NEW_WEIGHT × evidence_weight

new_mastery =
    MASTERY_OLD_WEIGHT × old_mastery
    + effective_new_weight × adjusted_score

new_mastery = clamp(new_mastery, 0, 1)
```

Cấu hình mặc định: `MASTERY_OLD_WEIGHT = 0.7`, `MASTERY_NEW_WEIGHT = 0.3`.

Chỉ giá trị mastery cuối cùng mới được clamp. `adjusted_score` có thể > 1.0 khi `difficulty_multiplier` > 1.0 (câu khó).

### Difficulty multipliers (Trọng số độ khó)

| Difficulty (`QuestionDifficulty`) | Multiplier | Lý do |
| --- | --- | --- |
| `EASY` | `0.80` | Câu dễ mang lại ít bằng chứng mastery hơn |
| `MEDIUM` | `1.00` | Chuẩn |
| `HARD` | `1.15` | Câu khó trả lời đúng thể hiện hiểu sâu hơn |

> Cơ sở: Item Difficulty Weighting trong Item Response Theory (Lord, 1980).

### Evidence weight decay (Trọng số bằng chứng giảm dần — Anti-gaming)

Trả lời lại cùng một câu hỏi sẽ bị giảm trọng số bằng chứng:

| Lần trả lời (trên cùng câu hỏi) | Evidence weight |
| --- | --- |
| Lần 1 (câu mới) | `1.00` |
| Lần 2 (lặp lại) | `0.50` |
| Lần 3 trở đi | `0.25` |

Evidence weight giảm đóng góp của lần trả lời lặp khi tính dimension và đếm câu hỏi độc lập. Không cho phép việc học thuộc lòng câu trả lời cũ thỏa mãn điều kiện câu hỏi độc lập.

> Cơ sở: Testing Effect — diminishing returns of repeated testing (Roediger & Karpicke, 2006).

## Dimension routing (Định tuyến chiều đánh giá theo loại câu hỏi)

Hệ thống lưu trữ 3 điểm thành phần riêng biệt trên `MasteryState`, mỗi điểm được cập nhật bởi loại câu hỏi tương ứng:

| Loại câu hỏi (`QuestionType`) | Chiều được cập nhật (`MasteryState` field) | Công thức đầu vào |
| --- | --- | --- |
| `RECALL`, `SCAFFOLDED_RECALL` | `recall_score` | `correctness` |
| `EXPLAIN` | `understanding_score` | `(coverage + reasoning) / 2` |
| `APPLY`, `APPLICATION_DIAGNOSIS`, `TRANSFER` | `application_score` | `application` |

Mỗi chiều được cập nhật bằng EMA tương tự mastery tổng: `update_dimension(current, observation, evidence_weight)`.

Khi câu hỏi APPLY/TRANSFER có `overall_score >= 0.60` → đặt `has_application_evidence = True`.

> Cơ sở: ICAP Framework (Chi & Wylie, 2014) — mỗi chiều phản ánh mức độ tham gia nhận thức khác nhau và phải được theo dõi độc lập.

## Recall versus understanding

- **`recall_score`** đo lường khả năng truy xuất đúng sự kiện hoặc mối quan hệ.
- **`understanding_score`** đo lường coverage + giải thích cách thức hoặc lý do các ý tưởng liên kết.
- Một người học có thể nhớ thuật ngữ nhưng không giải thích được cơ chế.
- **`application_score`** được theo dõi riêng để điểm recall cao không che lấp khoảng cách recall–application.

## `MASTERED` condition (Cổng chốt thông thạo)

Tất cả 4 điều kiện phải đồng thời đạt (Conservative Mastery Gating):

```text
mastery_score >= MASTERY_THRESHOLD            (mặc định: 0.80)
AND question_evidence_count >= MIN_QUESTIONS_FOR_MASTERY  (mặc định: 3)
AND has_application_evidence = true           (bắt buộc khi require_application_for_mastery = true)
AND has_critical_misconception = false        (không tồn tại misconception severity = "critical")
```

Không có 1 câu trả lời đơn lẻ nào có thể đánh dấu một Knowledge Unit là `MASTERED`.

### Mastery status (`MasteryStatus`)

| Status | Điều kiện |
| --- | --- |
| `NOT_STARTED` | `question_evidence_count = 0` và `mastery_score < threshold` |
| `IN_PROGRESS` | Đã trả lời ít nhất 1 câu nhưng chưa đạt đủ 4 gate |
| `MASTERED` | Đạt đủ cả 4 điều kiện |

> Cơ sở: Conservative mastery gating yêu cầu nhiều bằng chứng độc lập giảm false positive xuống < 5% (Corbett & Anderson, 1995, Knowledge Tracing).

## Misconception tracking

- Khi evaluation có `detected_misconceptions` không rỗng → ghi nhận misconception vào DB (`severity = "medium"`).
- Khi `overall_score >= 0.75` và không có misconception mới → tự động resolve các misconception đang active.
- Khi số lần xuất hiện của cùng một misconception `>= agent_trigger_wrong_count` → kích hoạt `ACTIVATE_TUTOR_AGENT` (nếu `agent_enabled = true`) hoặc `DETERMINISTIC_REMEDIATION`.

## Confidence handling

- Evaluator confidence thấp không được tự động tạo critical misconception mới.
- Hành động tiếp theo trở thành `ASK_CLARIFICATION` hoặc manual review theo policy.
- Điểm không hợp lệ hoặc ngoài phạm vi bị reject trước khi lưu (Pydantic validation).
- Confidence là metadata đánh giá; không nhân trực tiếp vào correctness trừ khi có ADR thay đổi.
- Phát hiện nghiêm trọng mâu thuẫn sẽ được giữ lại để review thay vì bị ghi đè.

## Update invariants

- Lưu trữ nguyên tử (atomic): answer attempt, rubric ID, evaluation, previous mastery, new mastery, và rule outcome.
- Clamp tất cả điểm tính toán vào `[0, 1]`.
- Evaluation lỗi hoặc schema-invalid không được cập nhật mastery.
- Chỉ tính lại status SAU KHI attempt hợp lệ đã được lưu.
- `question_evidence_count` chỉ tăng khi `prior_user_attempts == 0` (câu hỏi hoàn toàn mới, không phải retry).
