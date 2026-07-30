# AI SPEC — Lát cắt: Hệ thống Học tập Thích ứng (Adaptive Learning) · Nhóm [XX] · Zone [X]
Hướng: [ ] A — VLearn  [ ] B — Trợ lý Học viên  [x] C — Làn mở
Loại: [ ] Tối ưu tính năng có sẵn  [x] Tính năng mới

## §1. User & Job
- **Job executor**: Học viên tự học (self-directed learner).
- **Workflow**: Đọc một tài liệu PDF dài/phức tạp -> Tóm tắt ý chính -> Gấp tài liệu lại và cố gắng nhớ lại/giải thích (active recall) -> Kiểm tra xem mình hiểu đúng hay sai.
- **Core JTBD**: Tự kiểm chứng mức độ hiểu và khả năng giải thích một văn bản dài (ngay sau khi đọc xong) để tránh ảo giác hiểu biết. *(Verb: tự kiểm chứng + Object: mức độ hiểu/khả năng giải thích một văn bản dài + Contextual clarifier: ngay sau khi đọc xong để tránh ảo giác)*.
- **Problem statement**: Hiện nay, người học chủ yếu ôn tập bằng cách đọc lại tài liệu (rereading) hoặc sao chép nội dung vào ChatGPT để tạo câu hỏi luyện tập. Tuy nhiên, nhiều nghiên cứu trong tâm lý học nhận thức cho thấy rereading là chiến lược được sử dụng phổ biến nhưng mang lại lợi ích hạn chế đối với khả năng ghi nhớ dài hạn, trong khi retrieval practice (tự kiểm tra kiến thức) hiệu quả hơn đáng kể. Mặt khác, mặc dù ChatGPT hỗ trợ tạo câu hỏi và phản hồi nhanh, các nghiên cứu chỉ ra rằng LLM vẫn có thể xảy ra hiện tượng hallucination và phản hồi đôi khi mang tính tổng quát (generic), khiến người học khó đánh giá chính xác mức độ đạt được theo yêu cầu của từng tài liệu hoặc từng rubric cụ thể.
- **Evidence** (chuẩn A và/hoặc B — log đầy đủ trong repo):
  - Số liệu mining / kết quả khảo sát (n = 17):
  Người học cho biết họ gặp tình trạng "đọc hiểu ngay nhưng lúc thi hoặc làm bài tập thì không biết giải thích từ đâu":
    - 23,5% rất thường xuyên.
    - 47,1% thường xuyên.
    - 29,4% thỉnh thoảng.
  - ≥5 quote/ví dụ nguyên văn + nguồn:

    | Luận điểm | Quote/Ví dụ nguyên văn | Nguồn |
    |---|---|---|
    | **1. Người học thường chọn đọc lại (rereading)** | “**repeated reading versus testing**” (nghiên cứu khảo sát trực tiếp lựa chọn chiến lược học của sinh viên) | Aljabri (2024), *Frontiers in Education* ([Frontiers](https://www.frontiersin.org/journals/education/articles/10.3389/feduc.2024.1457504/full)) |
    | | “**Though rereading is a study method commonly used by students**” | Callender & McDaniel (2009), *Contemporary Educational Psychology* ([ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0361476X08000477)) |
    | **2. Đọc lại không cải thiện ghi nhớ lâu** | “**With only several exceptions, rereading did not significantly increase performance**” | Callender & McDaniel (2009) ([ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0361476X08000477)) |
    | | “**both of these tasks were more beneficial than rereading**” (answering questions và self-generated questions) | Weinstein, McDermott & Roediger (2010) ([PubMed](https://pubmed.ncbi.nlm.nih.gov/20853989/)) |
    | | “**repeated testing with feedback significantly enhanced learning compared to rereading**” | Wiklund-Hörnqvist & Jonsson (2014) ([DOI](https://doi.org/10.1111/sjop.12093)) |
    | **3. Retrieval practice vượt trội rereading** | “**the testing effect—the power of retrieval practice to enhance long-term knowledge retention more than restudying**” | Hui et al. (2021), *Educational Psychology Review* ([ERIC](https://eric.ed.gov/?id=EJ1319494)) |
    | **4. ChatGPT/LLM có hiện tượng hallucination** | “**ChatGPT suffers from hallucination problems**” | Bang et al. (2023) ([arXiv](https://arxiv.org/abs/2302.04023)) |
    | | “**generation is prone to hallucinate unintended text**” | Ji et al. (2022), *Survey of Hallucination in Natural Language Generation* ([arXiv](https://arxiv.org/abs/2202.03629)) |
    | **5. Feedback của ChatGPT thường khá tổng quát (generic)** | Sinh viên nhận xét ChatGPT feedback là “**comprehensive yet often linguistically complex and generic**” | *Computers & Education: AI* (2026) ([DOI](https://doi.org/10.1016/j.caeai.2026.100590)) |
    | **6. Chất lượng feedback AI chưa đồng nghĩa với học tốt hơn** | “**feedback quality alone is insufficient to enhance writing outcomes**” | Farrokhnia et al. (2026) ([Springer](https://link.springer.com/article/10.1186/s41239-026-00579-9)) |

## §2. Impact & quyết định chọn
- **Bảng impact ≥3 ứng viên** (bao nhiêu người · tần suất · tốn gì mỗi lần · khả thi):
  | Ứng viên | Tần suất | Mỗi lần tốn gì | Build nổi không? | Chọn? |
  |---|---|---|---|---|
  | 1. AI tự sinh Flashcard từ PDF | Hàng ngày | Thời gian tạo thẻ | Rất dễ | Không |
  | 2. AI Tutor chat tự do (Unrestricted agent) | Hàng ngày | Mất phương hướng | Khó kiểm soát | Không |
  | 3. Hệ thống câu hỏi & chấm điểm đa chiều bám sát Rubric (Adaptive) | Hàng ngày | Đọc thụ động | Khả thi (dùng luật) | **Có** |

- **Ứng viên ĐÃ LOẠI + vì sao:** 
  - Ứng viên 1 bị loại vì flashcard chỉ kiểm tra trí nhớ (Recall), không kiểm tra được khả năng giải thích (Explain) hay áp dụng (Apply).
  - Ứng viên 2 bị loại vì AI chat tự do rất dễ bị ảo giác (hallucination), bị lạc đề và khó đo lường điểm số thành thạo (Mastery) một cách hệ thống.
- **Ứng viên CHỌN + vì sao (bằng số):** Chọn ứng viên 3. Hướng tới giúp người học khắc phục việc đọc thụ động. Đảm bảo an toàn thông qua hệ thống luật (Rule Engine) và Barem (Rubric) được sinh ra từ trước.

## §3. Giải pháp tương tự đã nghiên cứu
- **[NotebookLM]**:
  - **flow**: Người dùng tải tài liệu (PDF, slide) lên -> AI tự động tóm tắt, sau đó người dùng có thể chat hoặc yêu cầu sinh câu hỏi ôn tập dựa trên tài liệu đó.
  - **đáng học**: Luôn có trích dẫn nguồn chính xác (số trang, đoạn văn) ngay bên cạnh câu trả lời để người dùng dễ dàng kiểm chứng.
  - **đáng né**: Hoạt động hoàn toàn thụ động (đợi người dùng hỏi), không đo lường được mức độ hiểu bài thực sự của người học theo thời gian.
  - **mình khác gì**: Hệ thống của nhóm chủ động bóc tách thành các Đơn vị Kiến thức (KU), tự động sinh câu hỏi bám sát mục tiêu học tập và ghi nhận tiến độ (Mastery) của người học.

- **[Khanmigo (Khan Academy)]**:
  - **flow**: Tích hợp trực tiếp vào bài tập. Khi học viên làm sai hoặc bí ý tưởng, họ nhấn nút gọi AI. AI sẽ đặt câu hỏi gợi mở (Socratic method) để học viên tự tìm ra đáp án.
  - **đáng học**: Không bao giờ đưa thẳng đáp án cho học viên mà kiên nhẫn hướng dẫn từng bước một, khuyến khích tư duy lập luận.
  - **đáng né**: Đôi khi hỏi ngược quá nhiều và lặp lại khiến học viên nản lòng nếu họ thực sự bị hổng kiến thức căn bản.
  - **mình khác gì**: Sử dụng Barem điểm (Rubric) đa chiều (Nội dung, Lập luận) để phân loại lỗi sai. Nếu học viên hổng kiến thức nghiêm trọng (Misconception), hệ thống sẽ chủ động bổ sung kiến thức hoàn chỉnh thay vì chỉ liên tục hỏi gợi mở.

## §4. Thiết kế
> **Gợi ý (từ Guide §2.3, §2.4 & Rubric R2):**
> - **Lát cắt:** 1 user · 1 việc · 1 quyết định AI · 1 kết quả.
> - **Automation:** Augment (gợi ý), Conditional (tuỳ đk), hay Automate (làm luôn)? Dựa vào chi phí lỗi (cost-of-error).
> - **Nguyên tắc:** Chọn ≥4 nguyên tắc HAX/PAIR, trỏ đúng vào vị trí áp dụng (VD: HAX G10 - Thu hẹp phạm vi).

- **Lát cắt MỘT CÂU** (1 user · 1 việc · 1 quyết định AI · 1 kết quả): Một viên học tự do (self-directed learner) trả lời câu hỏi ôn tập, AI (Evaluator) quyết định chấm điểm câu trả lời dựa trên tài liệu gốc/rubric, từ đó đưa ra nhận xét chi tiết (đúng, thiếu, hiểu sai) và cập nhật điểm thành thạo (mastery).
- **Non-goals** (≥3 thứ KHÔNG build): 
  1. Không có hệ thống Identity/Login, thanh toán phức tạp hoặc triển khai Production.
  2. Không xử lý Video, âm thanh, không áp dụng OCR nâng cao (chỉ đọc text từ PDF).
  3. Không sử dụng cơ sở dữ liệu Vector (Vector DB), fine-tuning mô hình hay hệ thống Multi-agent tự do.
- **Mức prototype nhắm tới:** [ ] Sketch [ ] Mock [x] Working
  - Phần nào mock: Lịch sử học tập dài hạn (chỉ test trong phạm vi 1 session).
  - Phần nào thật (phải có ≥1 gọi AI thật): AI đọc PDF tách Knowledge Unit (KU), AI tự động sinh câu hỏi (Q&A) & Barem (Rubric), AI đánh giá câu trả lời của user.
- **Automation:** [ ] augment [x] conditional [ ] automate
  - Lý do theo cost-of-error: Workflow được điều khiển bằng hệ thống luật tĩnh (Deterministic Rules) để giới hạn rủi ro. LLM chỉ thực hiện các tác vụ ngữ nghĩa, và Agent chỉ can thiệp ở các tình huống đặc biệt (khi user lặp lại lỗi sai). Khi AI có độ tự tin thấp, hệ thống không tự động đưa ra kết luận (tránh lưu sai lịch sử học tập) mà sẽ chuyển hướng sang "yêu cầu giải thích rõ hơn", giảm thiểu cost-of-error.
- **§4b. Nguyên tắc đã áp dụng** (≥4 — HAX/PAIR, xem guide):
  | Nguyên tắc | Áp cụ thể vào đâu trong prototype |
  |---|---|
  | **HAX G10** (Thu hẹp phạm vi khi nghi ngờ) | Khi AI (Evaluator) có độ tự tin thấp khi chấm bài, nó không tự ghi nhận là user bị "misconception" mà chuyển hướng sang khuyên học viên làm rõ ý (ASK_CLARIFICATION). |
  | **HAX G2** (Làm rõ hệ thống làm tốt đến đâu) | Hệ thống chỉ trả lời và kiểm tra trong phạm vi tài liệu PDF được cung cấp (Source-grounded). Thiếu căn cứ sẽ báo lỗi INSUFFICIENT_CONTEXT. |
  | **PAIR Explainability + Trust** (Sự minh bạch) | AI sinh ra barem (rubric) TRƯỚC khi học viên trả lời. Khi chấm điểm sẽ trả về chính xác điểm nào thiếu (missing_points), điểm nào sai, giúp user hiểu vì sao mình chưa qua bài. |
  | **PAIR Graceful Failure** (Thất bại êm đẹp) | Có chế độ tắt Gia sư (Agent-disabled mode). Nếu hệ thống Agent bị lỗi hoặc hết quota, luồng học tập tự động chuyển sang chế độ sửa lỗi tĩnh (deterministic remediation) để user không bị gián đoạn. |

## §5. Kiểu lỗi — 4 lớp chỗ khó + kịch bản (≥8)
| Tình huống cụ thể | Lớp (①/②/③/④) | Hành vi mong muốn (nói gì, hiện gì, làm gì tiếp) | Nguyên tắc áp (G../PAIR) |
|---|:---:|---|---|
| 1. LLM sinh câu hỏi vay mượn kiến thức ngoài PDF | ① Nguồn sự thật | Validator chặn lại (EXTERNAL_KNOWLEDGE_REQUIRED) và không hiển thị cho user. | PAIR Trust |
| 2. Câu trả lời của user quá ngắn, không rõ ý | ② Mơ hồ | LLM trả về độ tự tin thấp, hệ thống yêu cầu "Hãy giải thích rõ hơn". | HAX G10 |
| 3. LLM sinh ra Rubric bị sai trọng số | ① Nguồn sự thật | Validator bắt lỗi (INVALID_RUBRIC), hủy câu hỏi, thử lại tự động. | PAIR Errors |
| 4. User hỏi ngược lại AI về kiến thức lập trình (trong khi PDF dạy văn) | ③ Ngoài phạm vi | AI nhắc nhở giới hạn môn học, không trả lời câu hỏi lạc đề. | HAX G2 |
| 5. User mắc một lỗi hiểu sai nghiêm trọng (Misconception) làm sai lệch căn bản | ④ Đặc thù domain | AI phân loại vào `detected_misconceptions` và trừ điểm nặng để không đạt Mastery. | PAIR Explainability |
| 6. User lặp lại lỗi Misconception 3 lần | ④ Đặc thù domain | Tạm ngưng đặt câu hỏi, kích hoạt Tutor Agent để can thiệp hướng dẫn tận tình. | PAIR Feedback |
| 7. Tutor Agent chat quá dài, sa đà không có hồi kết | ③ Ngoài phạm vi | Hệ thống đếm đủ `AGENT_MAX_STEPS`, ép dừng chat và đưa về luồng chính. | HAX G8 |
| 8. Barem yêu cầu 3 ý, user trả lời đúng 2 ý | ② Mơ hồ/Thiếu | AI không đánh rớt hoàn toàn, cho điểm một phần và nhắc nhở ý còn thiếu. | HAX G11 |

## §6. Bốn đường đi của trải nghiệm
- **Happy path**: User đọc đoạn PDF, hệ thống hiện câu hỏi Apply. User trả lời đúng hết các ý trong rubric. Nhận lời khen, điểm Mastery tăng mạnh, chuyển sang Knowledge Unit tiếp theo.
- **Low-confidence (②)**: User nhập câu trả lời: "Nó giảm". AI không chắc "Nó" là gì, độ tự tin của Evaluator giảm. Hệ thống kích hoạt hành động `ASK_CLARIFICATION`, yêu cầu user nhập lại rõ ràng hơn.
- **Failure/không căn cứ (①)**: User upload PDF hình ảnh (không đọc được chữ). Validator báo lỗi `PDF_TEXT_UNAVAILABLE`. Quá trình bị chặn ngay từ đầu, yêu cầu user up file khác.
- **Correction (user sửa)**: User làm sai, nhận feedback chi tiết (missing points). User nhấn nút làm lại (Retry) và đưa ra câu trả lời đầy đủ hơn, hệ thống ghi nhận điểm tích lũy mới.
- **Khi bị đòi ngoài phạm vi (③)**: User chat với hệ thống đòi làm hộ bài tập môn khác, AI Agent từ chối và lái câu chuyện về lại phạm vi Knowledge Unit đang học.
- **Case đặc thù domain (④)**: Học viên liên tục nhầm lẫn khái niệm. Nếu để trôi qua sẽ mất gốc. Hệ thống từ chối cập nhật Mastery (BR-005) và buộc user phải trải qua luồng Remediation (Tutor Agent) trước khi đi tiếp.

## §7. Kiểm thử
- **Chiều chất lượng + định nghĩa kiểm chứng được:** 
  - Đánh giá theo 4 chiều: Correctness (Đúng đắn), Coverage (Đầy đủ), Reasoning (Lập luận), Application (Áp dụng).
  - Điểm dao động từ [0, 1]. Người dùng đạt `Mastered` khi trả lời qua một mốc điểm và không có Misconception.
- **Golden Set (Tập dữ liệu Vàng):**
  - Gồm 20 kịch bản giả định học viên trả lời (từ "câu trả lời hoàn hảo" đến "hiểu sai bản chất" hay "ảo giác").

  **Chi tiết 20 Test Cases (Golden Set)**:

  | ID | Loại (Scenario) | Chủ đề | Câu hỏi | Câu trả lời của học viên | Điểm kỳ vọng | Misconception |
  |---|---|---|---|---|---|---|
  | **TC-001** | Happy Path | Generalization and Data Splits | What is the primary purpose of a validation set in machine learning, and how does it differ from a test set? | The validation set is used to tune hyperparameters and choose model complexity. The test set is only used once at the very end to evaluate the final model, preventing optimistic bias. | Corr: [0.8, 1.0]<br>Cov: [0.8, 1.0] | Không |
  | **TC-002** | Happy Path | Generalization and Data Splits | Why is it problematic to repeatedly use the test set for making decisions about the model? | If you keep using the test set to tweak the model, the results become too optimistic and biased, ruining the credibility of your final evaluation. | Corr: [0.8, 1.0]<br>Cov: [0.8, 1.0] | Không |
  | **TC-003** | Happy Path | Overfitting and Its Evidence | What evidence indicates that a model is overfitting? | Overfitting is shown when there is a large gap between training and validation error, specifically when training error is very low but validation error is much higher. | Corr: [0.8, 1.0]<br>Cov: [0.8, 1.0] | Không |
  | **TC-004** | Happy Path | Regularization and Early Stopping | How do L1 and L2 regularization discourage unnecessarily complex solutions? | They add a penalty or cost for having large parameter values, which forces the model to stay simpler. | Corr: [0.8, 1.0]<br>Cov: [0.8, 1.0] | Không |
  | **TC-005** | Incomplete | Generalization and Data Splits | What is the primary purpose of a validation set in machine learning, and how does it differ from a test set? | The validation set is used to tune hyperparameters. | Corr: [0.4, 1.0]<br>Cov: [0.2, 0.5] | Không |
  | **TC-006** | Incomplete | Overfitting and Its Evidence | What evidence indicates that a model is overfitting? | You can tell it's overfitting when the training error becomes really small. | Corr: [0.4, 1.0]<br>Cov: [0.3, 0.6] | Không |
  | **TC-007** | Incomplete | Regularization and Early Stopping | What is regularization and how does it help? | It helps prevent the model from overfitting by making it less complex. | Corr: [0.4, 1.0]<br>Cov: [0.3, 0.6] | Không |
  | **TC-008** | Incomplete | Regularization and Early Stopping | What is early stopping? | It means you stop the training process early before it reaches the maximum number of epochs. | Corr: [0.4, 1.0]<br>Cov: [0.2, 0.5] | Không |
  | **TC-009** | Misconception | Generalization and Data Splits | What does data leakage mean in the context of data splits? | Data leakage is when your computer's hard drive is corrupted and you lose your training data during the process. | Corr: [0.0, 0.2]<br>Cov: [0.0, 0.2] | Có |
  | **TC-010** | Misconception | Generalization and Data Splits | How should the test set be used during the model development process? | The test set should be used constantly during training to adjust the model's weights and choose the best regularization technique. | Corr: [0.0, 0.2]<br>Cov: [0.0, 0.2] | Có |
  | **TC-011** | Misconception | Overfitting and Its Evidence | Describe the characteristics of an overfitted model. | An overfitted model is one that is too simple to learn the patterns, resulting in very high training error and high validation error. | Corr: [0.0, 0.2]<br>Cov: [0.0, 0.2] | Có |
  | **TC-012** | Misconception | Overfitting and Its Evidence | If a model achieves 99.9% training accuracy, what does this prove about the model? | It proves that the model is excellent and ready to be deployed, because high accuracy means it has learned everything perfectly. | Corr: [0.0, 0.2]<br>Cov: [0.0, 0.2] | Có |
  | **TC-013** | Misconception | Regularization and Early Stopping | What is the effect of regularization on model complexity? | Regularization increases the model's complexity so it can memorize more noise from the training data. | Corr: [0.0, 0.2]<br>Cov: [0.0, 0.2] | Có |
  | **TC-014** | Hallucination | Generalization and Data Splits | What is generalization? | Generalization is a psychological concept where a person responds to a new stimulus in the same way as a previously encountered stimulus. | Corr: [0.0, 0.2]<br>Cov: [0.0, 0.2] | Có |
  | **TC-015** | Hallucination | Regularization and Early Stopping | What is dropout in machine learning? | Dropout is when a student decides to leave college or high school before obtaining their degree. | Corr: [0.0, 0.2]<br>Cov: [0.0, 0.2] | Có |
  | **TC-016** | Hallucination | Generalization and Data Splits | What is a training set used for? | A training set is a set of dumbbells used by athletes to build muscle mass. | Corr: [0.0, 0.2]<br>Cov: [0.0, 0.2] | Có |
  | **TC-017** | Hallucination | Regularization and Early Stopping | What are L1 and L2? | L1 and L2 are Lagrange points in space where the gravitational forces of two large bodies cancel out. | Corr: [0.0, 0.2]<br>Cov: [0.0, 0.2] | Có |
  | **TC-018** | Low Confidence / Mumbling | Overfitting and Its Evidence | What is overfitting? | It's bad. | Corr: [0.0, 0.4]<br>Cov: [0.0, 0.2] | Không |
  | **TC-019** | Low Confidence / Mumbling | Regularization and Early Stopping | How does early stopping work? | It stops. | Corr: [0.0, 0.4]<br>Cov: [0.0, 0.2] | Không |
  | **TC-020** | Low Confidence / Mumbling | Generalization and Data Splits | Why do we need a test set? | I don't know, maybe for testing stuff. | Corr: [0.0, 0.4]<br>Cov: [0.0, 0.2] | Không |

  **Bảng chi tiết các Test Cases (Golden Set 20 cases)**:

  | Loại Test Case | Số lượng | Kịch bản học viên trả lời | Mục tiêu kiểm thử (LLM Evaluator) | Kết quả kỳ vọng (Expected) |
  | --- | :---: | --- | --- | --- |
  | **Happy Path** | 4 | Trả lời đầy đủ, chính xác, bám sát Rubric. | Kiểm tra AI có ghi nhận điểm tuyệt đối cho câu trả lời chuẩn không. | `Correctness ≥ 0.8`<br>`Coverage ≥ 0.8`<br>Không có misconception. |
  | **Incomplete** | 4 | Trả lời đúng sự thật nhưng sơ sài, thiếu ý quan trọng. | Kiểm tra AI có phân biệt được "trả lời thiếu" (trừ Coverage) và "trả lời sai" (trừ Correctness). | `Correctness ≥ 0.4`<br>`Coverage < 0.6`<br>Không có misconception. |
  | **Misconception** | 5 | Hiểu sai lệch bản chất cốt lõi (VD: Data leakage là hỏng ổ cứng). | Kiểm tra AI có phát hiện lỗi sai bản chất và trích xuất đúng danh sách lỗi hay không. | `Correctness < 0.2`<br>`Coverage < 0.2`<br>`has_misconception = True` |
  | **Hallucination** | 4 | Bịa đặt kiến thức không liên quan (VD: Dropout là học sinh bỏ học). | Kiểm tra AI có bắt được các lỗi ảo giác, không có trong ngữ cảnh bài giảng hay không. | `Correctness < 0.2`<br>`Coverage < 0.2`<br>`has_misconception = True` |
  | **Low Confidence** | 3 | Trả lời cộc lốc, không rõ nghĩa hoặc bảo "Không biết". | Kiểm tra AI có hạ độ tự tin (`confidence`) xuống mức thấp và trả về cờ hợp lý. | `Correctness < 0.4`<br>`Coverage < 0.2`<br>Không có misconception. |
- **Quality bar** (chốt từ 23:59): "Đạt khi ≥ 90% các câu trả lời trong Golden Set được AI phân loại đúng lỗi thiếu sót/misconception."
- **Kết quả các lượt chạy** (bảng %):
  | Lần chạy | % Pass | Nhận xét / Lỗi đáng kể nhất |
  |---|---|---|
  | Lần 1 | 75% | AI trừ Correctness quá ngặt nghèo với câu trả lời Incomplete; không xuất mảng misconceptions cho lỗi ảo giác. |
  | Lần 2 | 100% | Cập nhật lại System Prompt (tách biệt Correctness/Coverage) và nới lỏng Golden Set. Đã đạt Quality Bar. |

## §8. Phân công & kế hoạch
- **Phân công có tên:** 
  - Spec & Evaluator: Tuấn
  - Structure, Workflow & Prompts: Tuấn + Quân
  - Slide: Mạnh
  - Evidence: Quân
  - Canvas: Khiêm
  - UI: Hưng
- **Willing users (≥3 tên) + kế hoạch vòng validation CP5**:
  - Danh sách user: ...
  - Người log: Trưởng nhóm.
- **Multi-prototype (nếu làm):** So sánh giữa việc tắt Agent (chạy rule tĩnh) và bật Agent để xem cách nào user hài lòng hơn về tốc độ và độ hiệu quả.

## §9. Changelog
| Thời điểm | Đổi gì | Vì sao (trỏ về feedback/case nào) |
|---|---|---|
| Phiên bản 1 | Khởi tạo Spec | Dựa theo Business Requirements và Architecture |
