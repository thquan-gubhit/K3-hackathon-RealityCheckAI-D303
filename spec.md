# AI SPEC — [Tên lát cắt] · Nhóm [XX] · Zone [X]
Hướng: [ ] A — VLearn  [ ] B — Trợ lý Học viên  [ ] C — Làn mở
Loại: [ ] Tối ưu tính năng có sẵn  [ ] Tính năng mới

> **Lưu ý:** Xoá các đoạn gợi ý (in nghiêng blockquote) khi nhóm bạn đã điền xong.

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
