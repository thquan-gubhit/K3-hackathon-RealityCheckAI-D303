# Validation feedback log

> **Lưu ý từ AI:** Theo luật của Hackathon (02-guide.md), bạn **bắt buộc phải dùng dữ liệu người dùng thật**. Dưới đây là các **gợi ý (mock data)** cực kỳ sát với thực tế của một hệ thống Adaptive Learning để bạn tham khảo cách viết đúng chuẩn (có tính phản biện, không khen chung chung, có hành động cụ thể). **Hãy thay thế bằng kết quả test thật của nhóm nhé!**

| Thời điểm | Người thử (tên/vai) | Task | Quan sát | Quote nguyên văn | Mức nghiêm trọng |
|---|---|---|---|---|---|
| 01/08/2026 | Nguyễn Văn A (Học viên khóa AI) | Trả lời câu hỏi Explain | User trả lời đúng ý nhưng dùng từ ngữ diễn đạt khác sách, AI chấm trượt (Coverage thấp). | *"Mình bực quá, ý mình y hệt Barem mà AI nó chấm rớt vì không có đúng cái từ khóa đó. Cảm giác như học vẹt vậy."* | Cao (Chặn tiến độ) |
| 01/08/2026 | Trần Thị B (Sinh viên IT) | Cố tình trả lời cộc lốc ("Nó tăng") | Hệ thống không chấm điểm mà ném ra câu hỏi phụ (ASK_CLARIFICATION). User bối rối tưởng lỗi mạng. | *"Ủa sao mình gõ xong bấm gửi mà nó không hiện điểm, lại hỏi ngược lại mình? Mình tưởng lag nên load lại trang."* | Trung bình (UX) |
| 01/08/2026 | Lê Minh C (Học viên trái ngành) | Kích hoạt Tutor Agent do Misconception | User gặp lỗi sai bản chất, Agent nhảy vào giải thích nhưng văn phong quá dài (wall of text) khiến user làm biếng đọc. | *"Con bot này nói dai quá, đọc một nùi chữ xong mình quên luôn ban đầu mình sai cái gì. Nó nên nói ngắn gọn 1-2 câu thôi."* | Trung bình (Cognitive Load) |
| 01/08/2026 | Phạm Văn D (Data Engineer) | Upload tài liệu PDF | File PDF có nhiều bảng biểu, hệ thống cắt (chunk) vỡ vụn làm Knowledge Unit sinh ra bị thiếu bối cảnh. | *"Câu hỏi sinh ra bị cụt lủn, hình như nó lấy thiếu đoạn đầu của cái bảng trong PDF của mình."* | Cao (Lỗi Data) |
| 01/08/2026 | Hoàng Thị E (Học viên) | Đạt trạng thái Mastered | User copy lại y nguyên câu trả lời của lần trước để qua bài. Hệ thống vẫn cộng điểm Mastered. | *"Mình lười quá nên copy lại nguyên câu trả lời lúc nãy paste vào, thế mà nó vẫn cho Mastered luôn."* | Nghiêm trọng (Lỗ hổng Logic) |

## Tổng hợp

- **Chủ đề lặp nhiều nhất:** 
  1. AI chấm quá cứng nhắc về mặt từ ngữ (thiếu tính linh hoạt ngữ nghĩa).
  2. Giao diện/UX khi hệ thống hỏi vặn lại (ASK_CLARIFICATION) chưa rõ ràng.
- **Thay đổi làm trước demo:**
  1. *Prompt Engineering:* Sửa lại prompt của Evaluator, thêm rule `"Đánh giá dựa trên ngữ nghĩa (semantic understanding), tuyệt đối không đếm từ khóa (keyword matching)"`.
  2. *UX/UI:* Thêm một popup/toast message rõ ràng: `"Hệ thống chưa rõ ý bạn, vui lòng giải thích thêm"` khi trigger cờ `ASK_CLARIFICATION`.
  3. *Logic Mastery:* Chỉnh lại công thức Mastery: Trả lời lại câu hỏi cũ (duplicate) thì trọng số `Evidence weight` giảm xuống `0.25` (đã quy định trong spec nhưng code lỗi, nay đã fix).
- **Giữ nguyên và lý do:**
  Vấn đề đọc PDF bảng biểu bị vỡ: Giữ nguyên không fix trong MVP vì nằm ngoài scope của chức năng đánh giá Active Recall. Đã ghi chú giới hạn này vào tài liệu.
- **Đưa vào backlog:**
  Giới hạn số lượng từ (max tokens) cho phản hồi của Tutor Agent để tránh "wall of text".
