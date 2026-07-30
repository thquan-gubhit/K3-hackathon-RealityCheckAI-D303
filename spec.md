# AI SPEC — [Tên lát cắt] · Nhóm [XX] · Zone [X]
Hướng: [ ] A — VLearn  [ ] B — Trợ lý Học viên  [ ] C — Làn mở
Loại: [ ] Tối ưu tính năng có sẵn  [ ] Tính năng mới


## §1. User & Job

- **Job executor + workflow:** Học viên đang trong buổi học trên VLearn, vừa gặp một khái niệm, đoạn chữ hoặc biểu đồ trên slide mà mình chưa hiểu. Họ bôi chọn đoạn và hỏi ngay trong trang; nếu câu trả lời chưa đủ, họ phải hỏi người khác, tự tìm kiếm hoặc bỏ qua để theo tiếp bài. Worksheet chi tiết: [`docs/jtbd-section1.md`](docs/jtbd-section1.md).
- **Core JTBD:** Làm rõ ngay đoạn bài học vừa gặp mà mình chưa hiểu để tiếp tục theo kịp buổi học.
- **Problem statement:** Hiện tại học viên dùng hộp hỏi đáp ngay trong trang vì nhanh và giữ được đoạn đang xem. Luồng này fail khi không truy được đúng nội dung, trả lời thiếu căn cứ hoặc dừng ở việc đưa lời giải mà không xác nhận người học đã hiểu; chuyển sang hỏi người khác hay tự tìm kiếm lại làm gián đoạn nhịp học, còn bỏ qua dễ để lại lỗ hổng.
- **Evidence** (mining data; phương pháp và giới hạn ghi đầy đủ tại [`docs/evidence-section1.md`](docs/evidence-section1.md)):
  - Trong 1.261 lượt hỏi của 369 học viên, proxy từ khóa xác định 578 lượt làm rõ nội dung (45,8%), đến từ 239 học viên (64,8%).
  - Trong 578 câu trả lời tương ứng, 156 câu (27,0%) không có citation và chỉ 1 câu (0,17%) đặt câu hỏi kiểm tra hiểu.
  - Rating chỉ có ở 30/578 lượt (5,2%); 14/30 là down-rating. Đây là mẫu tự chọn rất nhỏ nên chỉ dùng như tín hiệu phụ, không suy rộng cho toàn bộ người học.
  - Ví dụ nguyên văn + nguồn:
    1. “giải thích 4 chiến lược” — `C0002 / T0959`, trang 45.
    2. “tại sao có lưu ý như trang 25” — `C0004 / T0154`, trang 25.
    3. “Giải thích đoạn bôi đen ở Trang 15.” — `C0007 / T0020`, trang 15.
    4. “"Context" là gì” — `C0013 / T0990`, trang 31.
    5. “Designt Pattern ReAct là gì có lưu ý gì về nó?” — `C0015 / T0811`, trang 2.
    6. “Giải thích biều đồ đc bôi đỏ” — `C0023 / T0399`, trang 6.

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
