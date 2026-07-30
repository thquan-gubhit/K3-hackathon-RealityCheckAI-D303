# AI SPEC — [Tên lát cắt] · Nhóm [XX] · Zone [X]
Hướng: [ ] A — VLearn  [ ] B — Trợ lý Học viên  [ ] C — Làn mở
Loại: [ ] Tối ưu tính năng có sẵn  [ ] Tính năng mới


## §1. User & Job
> **Gợi ý (từ Guide §1.1, §1.3 & Rubric R1):**
> - **Job executor:** Một vai cụ thể (VD: học viên đang-trong-buổi-học), không phải "học viên nói chung".
> - **Core JTBD:** Viết thành một câu `verb + object + bối cảnh` (không có chữ AI hay tên sản phẩm).
> - **Problem statement:** Hiện tại họ giải quyết bằng gì? Nó fail ở đâu? Tại sao họ chưa bỏ nó?
> - **Evidence:** Phải đếm được. Khảo sát (≥20 người ngoài nhóm, ≥50% xác nhận) và/hoặc Mining data (đếm được, có phương pháp, ≥5 ví dụ).

- **Job executor + workflow** (đính kèm worksheet JTBD / ảnh sơ đồ): 
- **Core JTBD** (không tên sản phẩm/AI trong câu): 
- **Problem statement** (KHÔNG chữ AI): 
- **Evidence** (chuẩn A và/hoặc B — log đầy đủ trong repo): 
  - Số liệu mining / kết quả khảo sát (n = ?, % xác nhận): 
  - ≥5 quote/ví dụ nguyên văn + nguồn: 
    1. "[Quote 1]" - Nguồn: 
    2. "[Quote 2]" - Nguồn: 
    3. "[Quote 3]" - Nguồn: 
    4. "[Quote 4]" - Nguồn: 
    5. "[Quote 5]" - Nguồn: 

## §2. Impact & quyết định chọn
> **Gợi ý (từ Rubric R1):** Lập bảng ít nhất 3 ứng viên.

- **Bảng impact ≥3 ứng viên** (bao nhiêu người · tần suất · tốn gì mỗi lần · khả thi):
  | Ứng viên | Số người gặp (từ evidence) | Tần suất | Mỗi lần tốn gì | Build nổi không? | Chọn? |
  |---|---|---|---|---|---|
  | 1. | | | | | |
  | 2. | | | | | |
  | 3. | | | | | |

- **Ứng viên ĐÃ LOẠI + vì sao:** 
- **Ứng viên CHỌN + vì sao (bằng số):** 

## §3. Giải pháp tương tự đã nghiên cứu
> **Gợi ý (từ Guide §2.2):** Từng thành viên dùng 1 app (vd: ChatGPT study, NotebookLM...). Rút ra 1 điều học, 1 điều né.

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

- **Lát cắt MỘT CÂU** (1 user · 1 việc · 1 quyết định AI · 1 kết quả): Một người học tự do (self-directed learner) trả lời câu hỏi ôn tập, AI (Evaluator) quyết định chấm điểm câu trả lời dựa trên tài liệu gốc/rubric, từ đó đưa ra nhận xét chi tiết (đúng, thiếu, hiểu sai) và cập nhật điểm thành thạo (mastery).
- **Non-goals** (≥3 thứ KHÔNG build): 
  1. Không có hệ thống Identity/Login, thanh toán phức tạp hoặc triển khai Production.
  2. Không xử lý Video, âm thanh, không áp dụng OCR nâng cao (chỉ đọc text từ PDF).
  3. Không sử dụng cơ sở dữ liệu Vector (Vector DB), fine-tuning mô hình hay hệ thống Multi-agent tự do.
- **Mức prototype nhắm tới:** [ ] Sketch [ ] Mock [x] Working 
  - Phần nào mock: Lịch sử học tập dài hạn (chỉ test trong phạm vi 1 session), Hệ thống user login.
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
> **Gợi ý (từ Rubric R3):** 4 lớp bao gồm: ① Nguồn sự thật (bịa ra), ② Mơ hồ/thiếu thông tin, ③ Ngoài phạm vi, ④ Đặc thù domain.

| Tình huống cụ thể | Lớp (①/②/③/④) | Hành vi mong muốn (nói gì, hiện gì, làm gì tiếp) | Nguyên tắc áp (G../PAIR) |
|---|:---:|---|---|
| 1. | | | |
| 2. | | | |
| 3. | | | |
| 4. | | | |
| 5. | | | |
| 6. | | | |
| 7. | | | |
| 8. | | | |

## §6. Bốn đường đi của trải nghiệm
> **Gợi ý:** Viết ngắn gọn user flow hoặc cách AI ứng xử.

- **Happy path**: 
- **Low-confidence (②)**: 
- **Failure/không căn cứ (①)**: 
- **Correction (user sửa)**: 
- **Khi bị đòi ngoài phạm vi (③)**: 
- **Case đặc thù domain (④)**: 

## §7. Kiểm thử
> **Gợi ý (từ Rubric R4):** 
> - **Golden set:** ≥20 case (≥2 case/lớp khó, 8-10 thường, 2-4 hiếm, ≥10 từ chatlog). Đặt trong thư mục `eval/`.
> - **Quality bar:** Cam kết mốc % pass để nghiệm thu.

- **Chiều chất lượng + định nghĩa kiểm chứng được:** 
- **Golden set** (≥20 case theo cơ cấu trong guide §2.6, file trong eval/): 
- **Quality bar** (chốt từ 23:59, giữ nguyên sau đó): "Đạt khi ≥ ___% qua bộ, và ___"
- **Kết quả các lượt chạy** (bảng % — cập nhật đến trước CP6):
  | Lần chạy | % Pass | Nhận xét / Lỗi đáng kể nhất |
  |---|---|---|
  | Lần 1 | | |

## §8. Phân công & kế hoạch
> **Gợi ý (từ Guide §3.5):** Phân công cụ thể (ai làm spec, code, prompt, v.v.).

- **Phân công có tên:** 
  - Spec: 
  - Evidence: 
  - Prompt: 
  - Code: 
  - Demo: 
- **Willing users (≥3 tên) + kế hoạch vòng validation CP5** (3 câu hỏi, ai log):
  - Danh sách user: 
  - Người log: 
- **Multi-prototype (nếu làm):** trục khác biệt của ≥2 phương án + lý do chọn:

## §9. Changelog
> **Gợi ý:** Theo dõi các phiên bản, đặc biệt là những gì thay đổi sau khi Validate với user.

| Thời điểm | Đổi gì | Vì sao (trỏ về feedback/case nào) |
|---|---|---|
| | | |
