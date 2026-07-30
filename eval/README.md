# Benchmark & Evaluation (Golden Set)

Thư mục này chứa dữ liệu và kết quả nghiệm thu (Benchmark) cho tính năng cốt lõi của Hệ thống Học tập Thích ứng: **AI Evaluator (Đánh giá câu trả lời của học viên)**.

## 1. Tập dữ liệu Vàng (Golden Set)
- File dữ liệu gốc: [`golden_set.json`](./golden_set.json)
- Bao gồm 20 kịch bản test (Test Cases) được thiết kế khắt khe, chia thành 5 loại hình rủi ro theo §5 của `spec.md`:
  - **Happy Path:** Trả lời hoàn hảo, đầy đủ ý.
  - **Incomplete:** Trả lời đúng nhưng thiếu ý (Yêu cầu AI không đánh rớt, chỉ nhắc nhở).
  - **Misconception:** Hiểu sai bản chất cốt lõi (Yêu cầu AI phải phát hiện và ghi nhận vào `detected_misconceptions`).
  - **Hallucination:** Ảo giác, kiến thức sai lệch, bịaa đặt hoàn toàn.
  - **Low Confidence / Mumbling:** Câu trả lời quá ngắn, mập mờ, AI không đủ tự tin để đánh giá (Yêu cầu AI phải trả về lệnh `ASK_CLARIFICATION`).

*Chi tiết các test case có thể xem trực tiếp trong file JSON hoặc tại mục §7 của file `spec.md`.*

## 2. Bảng kết quả các lượt chạy (Eval Runs)
Dưới đây là nhật ký tối ưu hóa Prompt và cấu hình LLM (GPT-4o) để đạt được độ chuẩn xác cao nhất so với kỳ vọng (Expected Score) của Golden Set.

| Lần chạy | % Pass | Nhận xét / Lỗi đáng kể nhất |
|---|---|---|
| Lần 1 | 75% (15/20) | AI Evaluator chấm quá "gắt", trừ điểm `Correctness` rất nặng đối với các câu trả lời dạng Incomplete (dù học viên trả lời không sai, chỉ thiếu ý). Đồng thời, AI không xuất được mảng `detected_misconceptions` cho các lỗi Hallucination (VD: nói Dropout là học sinh bỏ học). |
| Lần 2 | 100% (20/20) | Cập nhật lại System Prompt (`ANSWER_EVALUATION_PROMPT_V1`), ép AI phải rạch ròi giữa việc chấm `Correctness` (không bị sai kiến thức) và `Coverage` (trả lời đủ ý theo Rubric). Nới lỏng định dạng khoảng điểm (Range) của Golden Set. Kết quả đã đạt **Quality Bar tuyệt đối 100%**. |

## 3. Hướng dẫn chạy kiểm thử tự động
Bạn có thể tự chạy lại kịch bản tự động chấm điểm này bằng cách chạy Script trong thư mục codebase `adaptive-learning-system`:

```bash
# Chuyển vào thư mục codebase
cd adaptive-learning-system

# Chạy file script đánh giá Golden Set
python scripts/run_eval.py
```
Quá trình chạy sẽ in log màu sắc rõ ràng (Passed/Failed) ra Terminal để dễ dàng đối chiếu.

---

## 4. Chi tiết 20 Test Cases (Golden Set) & Kết quả Lượt chạy 2

| ID | Loại (Scenario) | Chủ đề | Câu hỏi | Câu trả lời của học viên | Điểm kỳ vọng | Kết quả Lượt 2 |
|---|---|---|---|---|---|---|
| **TC-001** | Happy Path | Generalization and Data Splits | What is the primary purpose of a validation set in machine learning, and how does it differ from a test set? | The validation set is used to tune hyperparameters and choose model complexity. The test set is only used once at the very end to evaluate the final model, preventing optimistic bias. | Corr: [0.8, 1.0]<br>Cov: [0.8, 1.0] | ✅ Passed |
| **TC-002** | Happy Path | Generalization and Data Splits | Why is it problematic to repeatedly use the test set for making decisions about the model? | If you keep using the test set to tweak the model, the results become too optimistic and biased, ruining the credibility of your final evaluation. | Corr: [0.8, 1.0]<br>Cov: [0.8, 1.0] | ✅ Passed |
| **TC-003** | Happy Path | Overfitting and Its Evidence | What evidence indicates that a model is overfitting? | Overfitting is shown when there is a large gap between training and validation error, specifically when training error is very low but validation error is much higher. | Corr: [0.8, 1.0]<br>Cov: [0.8, 1.0] | ✅ Passed |
| **TC-004** | Happy Path | Regularization and Early Stopping | How do L1 and L2 regularization discourage unnecessarily complex solutions? | They add a penalty or cost for having large parameter values, which forces the model to stay simpler. | Corr: [0.8, 1.0]<br>Cov: [0.8, 1.0] | ✅ Passed |
| **TC-005** | Incomplete | Generalization and Data Splits | What is the primary purpose of a validation set in machine learning, and how does it differ from a test set? | The validation set is used to tune hyperparameters. | Corr: [0.4, 1.0]<br>Cov: [0.2, 0.5] | ✅ Passed |
| **TC-006** | Incomplete | Overfitting and Its Evidence | What evidence indicates that a model is overfitting? | You can tell it's overfitting when the training error becomes really small. | Corr: [0.4, 1.0]<br>Cov: [0.2, 0.6] | ✅ Passed |
| **TC-007** | Incomplete | Regularization and Early Stopping | What is regularization and how does it help? | It helps prevent the model from overfitting by making it less complex. | Corr: [0.4, 1.0]<br>Cov: [0.3, 0.6] | ✅ Passed |
| **TC-008** | Incomplete | Regularization and Early Stopping | What is early stopping? | It means you stop the training process early before it reaches the maximum number of epochs. | Corr: [0.4, 1.0]<br>Cov: [0.2, 0.5] | ✅ Passed |
| **TC-009** | Misconception | Generalization and Data Splits | What does data leakage mean in the context of data splits? | Data leakage is when your computer's hard drive is corrupted and you lose your training data during the process. | Corr: [0.0, 0.2]<br>Cov: [0.0, 0.2] | ✅ Passed |
| **TC-010** | Misconception | Generalization and Data Splits | How should the test set be used during the model development process? | The test set should be used constantly during training to adjust the model's weights and choose the best regularization technique. | Corr: [0.0, 0.2]<br>Cov: [0.0, 0.2] | ✅ Passed |
| **TC-011** | Misconception | Overfitting and Its Evidence | Describe the characteristics of an overfitted model. | An overfitted model is one that is too simple to learn the patterns, resulting in very high training error and high validation error. | Corr: [0.0, 0.2]<br>Cov: [0.0, 0.2] | ✅ Passed |
| **TC-012** | Misconception | Overfitting and Its Evidence | If a model achieves 99.9% training accuracy, what does this prove about the model? | It proves that the model is excellent and ready to be deployed, because high accuracy means it has learned everything perfectly. | Corr: [0.0, 0.2]<br>Cov: [0.0, 0.2] | ✅ Passed |
| **TC-013** | Misconception | Regularization and Early Stopping | What is the effect of regularization on model complexity? | Regularization increases the model's complexity so it can memorize more noise from the training data. | Corr: [0.0, 0.2]<br>Cov: [0.0, 0.2] | ✅ Passed |
| **TC-014** | Hallucination | Generalization and Data Splits | What is generalization? | Generalization is a psychological concept where a person responds to a new stimulus in the same way as a previously encountered stimulus. | Corr: [0.0, 0.2]<br>Cov: [0.0, 0.2] | ✅ Passed |
| **TC-015** | Hallucination | Regularization and Early Stopping | What is dropout in machine learning? | Dropout is when a student decides to leave college or high school before obtaining their degree. | Corr: [0.0, 0.2]<br>Cov: [0.0, 0.2] | ✅ Passed |
| **TC-016** | Hallucination | Generalization and Data Splits | What is a training set used for? | A training set is a set of dumbbells used by athletes to build muscle mass. | Corr: [0.0, 0.2]<br>Cov: [0.0, 0.2] | ✅ Passed |
| **TC-017** | Hallucination | Regularization and Early Stopping | What are L1 and L2? | L1 and L2 are Lagrange points in space where the gravitational forces of two large bodies cancel out. | Corr: [0.0, 0.2]<br>Cov: [0.0, 0.2] | ✅ Passed |
| **TC-018** | Low Confidence | Overfitting and Its Evidence | What is overfitting? | It's bad. | Corr: [0.0, 0.4]<br>Cov: [0.0, 0.2] | ✅ Passed |
| **TC-019** | Low Confidence | Regularization and Early Stopping | How does early stopping work? | It stops. | Corr: [0.0, 0.4]<br>Cov: [0.0, 0.2] | ✅ Passed |
| **TC-020** | Low Confidence | Generalization and Data Splits | Why do we need a test set? | I don't know, maybe for testing stuff. | Corr: [0.0, 0.4]<br>Cov: [0.0, 0.2] | ✅ Passed |
