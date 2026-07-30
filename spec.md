# AI SPEC — Reality Check AI · Nhóm [XX] · Zone [X]
Hướng: [x] A — VLearn  [ ] B — Trợ lý Học viên  [ ] C — Làn mở
Loại: [ ] Tối ưu tính năng có sẵn  [x] Tính năng mới


## §1. User & Job

- **Job executor + workflow:** Học viên tự học trên VLearn, vừa đọc xong một đơn vị kiến thức trong tài liệu dạng chữ và cần quyết định học tiếp hay ôn lại. Workflow đầy đủ: [`docs/jtbd-section1.md`](docs/jtbd-section1.md).
- **Core JTBD:** Kiểm chứng mình có thể nhớ, giải thích và áp dụng một đơn vị kiến thức sau khi đọc để quyết định học tiếp hay ôn lại.
- **Problem statement:** Hiện tại học viên thường đọc lại, tự tóm tắt, tự nghĩ câu hỏi hoặc dùng hộp hỏi đáp để tạo quiz vì các cách này nhanh và sẵn có. Chúng fail khi cảm giác quen thuộc bị nhầm với hiểu thật, câu hỏi hoặc tiêu chí chấm không ổn định, phản hồi không tách rõ ý đúng–thiếu–sai và quyết định học tiếp vẫn dựa nhiều vào cảm giác.
- **Evidence** (mining data; phương pháp, giới hạn và liên hệ prototype tại [`docs/evidence-section1.md`](docs/evidence-section1.md)):
  - Gán nhãn tay sau bước lọc từ khóa xác định 11/1.261 lượt (0,9%), từ 10/369 học viên (2,7%), chủ động xin quiz hoặc đưa cách hiểu ra để xác nhận. Đây là bằng chứng hành vi tồn tại, **không đủ để kết luận pain phổ biến**.
  - Trong toàn bộ 1.261 câu trả lời tutor, chỉ 3 câu (0,24%) chủ động hỏi kiểm tra hiểu và không câu nào ghi nhận misconception (`0/1.261`), cho thấy luồng hiện tại gần như không tạo vòng đánh giá–sửa sai.
  - Ví dụ nguyên văn + nguồn:
    1. “TẠO QUIZ ĐỂ TÔI HIỂU RÕ VÀ ÔN LẠI TOÀN BỘ SLIDE NÀY” — `C0063 / T0849`, trang 9.
    2. “dựa vào tài liệu này bạn hãy cho tôi bộ quizz liên quan” — `C0287 / T1113`, trang 47.
    3. “vậy prompt engineerig có phải là mô tả lại ngữ cảnh của câu để cho AI hiểu rõ hơn không” — `C0242 / T0720`, trang 4.
    4. “benchmark là gì? Mỗi đề bài thì phải tự tạo benchmark đúng không, cho ví dụ” — `C0343 / T0633`, trang 23.
    5. “tức là trang này đang nói đến việc nên kiểm định giả thuyết nào, nên kiểm chứng nào chứ ko phải là nên xây dựng sản phẩm nào đúng không” — `C0350 / T0521`, trang 13.
    6. “Có phải là một câu hỏi có 4 câu thì transformer sẽ xử lý đồng loạt 4 câu đó thay vì xử lý từng câu đúng k?” — `C0468 / T1015`, trang 22.

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

- **[Sản phẩm 1]**: flow: ... / đáng học: ... / đáng né: ... / mình khác gì: ...
- **[Sản phẩm 2]**: flow: ... / đáng học: ... / đáng né: ... / mình khác gì: ...

## §4. Thiết kế
> **Gợi ý (từ Guide §2.3, §2.4 & Rubric R2):**
> - **Lát cắt:** 1 user · 1 việc · 1 quyết định AI · 1 kết quả.
> - **Automation:** Augment (gợi ý), Conditional (tuỳ đk), hay Automate (làm luôn)? Dựa vào chi phí lỗi (cost-of-error).
> - **Nguyên tắc:** Chọn ≥4 nguyên tắc HAX/PAIR, trỏ đúng vào vị trí áp dụng (VD: HAX G10 - Thu hẹp phạm vi).

- **Lát cắt MỘT CÂU** (1 user · 1 việc · 1 quyết định AI · 1 kết quả): 
- **Non-goals** (≥3 thứ KHÔNG build): 
  1. 
  2. 
  3. 
- **Mức prototype nhắm tới:** [ ] Sketch [ ] Mock [ ] Working 
  - Phần nào mock: 
  - Phần nào thật (phải có ≥1 gọi AI thật): 
- **Automation:** [ ] augment [ ] conditional [ ] automate 
  - Lý do theo cost-of-error: 
- **§4b. Nguyên tắc đã áp dụng** (≥4 — HAX/PAIR, xem guide):
  | Nguyên tắc | Áp cụ thể vào đâu trong prototype |
  |---|---|
  | 1. | |
  | 2. | |
  | 3. | |
  | 4. | |

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
