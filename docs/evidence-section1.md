# Evidence log — §1 User & Job

## Câu hỏi nghiên cứu

Trong lúc học từ tài liệu, học viên có biểu hiện muốn **tự kiểm tra hoặc xác nhận mức độ hiểu**, và luồng hỏi–đáp hiện tại có tạo được vòng “trả lời → đánh giá → sửa chỗ hiểu sai” hay không?

## Nguồn và phạm vi

- Nguồn: `data/vlearn-pack/chatlog/chat_history_anonymized_for_hackathon.csv`.
- Khoảng thời gian: 22/07–29/07/2026.
- Quy mô: 2.522 message, tương ứng 1.261 lượt hỏi–đáp; 369 học viên; 585 hội thoại.
- Chỉ dùng message `role = student` để tìm nhu cầu; ghép câu trả lời bằng `turn_id`.
- Toàn bộ hội thoại trong pack có `conversation_mode = in_class`.

## Phương pháp mining

### Bước 1 — Lấy tập ứng viên

Tìm không phân biệt hoa/thường theo hai nhóm:

```regex
# Chủ động luyện tập
quiz|quizz|tạo.*câu hỏi|bộ câu hỏi|luyện đề|ôn (lại|tập)

# Đưa cách hiểu ra để xác nhận
có phải|tức là|đúng không|đúng k|phải không
```

### Bước 2 — Gán nhãn tay

Đọc phần yêu cầu thực tế của từng lượt và chỉ giữ khi:

1. học viên yêu cầu câu hỏi/quiz để tự luyện; hoặc
2. học viên trình bày một cách hiểu về kiến thức rồi yêu cầu xác nhận.

Loại các lượt mà từ khóa chỉ nằm trong đoạn slide được chọn, câu hỏi về danh tính hệ thống, kiểm tra độ chính xác của nguồn, hoặc prompt kiểm thử bảo mật.

Danh sách 11 lượt được giữ để có thể kiểm tra lại:

- Tự luyện/quiz: `C0063/T0849`, `C0287/T1113`, `C0573/T0257`, `C0573/T0907`.
- Xác nhận cách hiểu: `C0238/T0666`, `C0242/T0720`, `C0343/T0633`, `C0350/T0521`, `C0442/T0923`, `C0461/T0782`, `C0468/T1015`.

### Bước 3 — Kiểm tra khoảng trống của luồng hiện tại

Trên 1.261 câu trả lời tutor, đếm:

- `asked_check_question = True`;
- `misconceptions` khác `[]`.

## Kết quả

| Chỉ số | Kết quả |
|---|---:|
| Tổng lượt hỏi–đáp | 1.261 |
| Lượt được gán nhãn “tự luyện/xác nhận cách hiểu” | 11 (0,9%) |
| Học viên có ít nhất một lượt thuộc nhóm trên | 10/369 (2,7%) |
| Câu trả lời tutor chủ động hỏi kiểm tra hiểu | 3/1.261 (0,24%) |
| Câu trả lời có ghi nhận misconception | 0/1.261 (0%) |

Tỷ lệ 0,9% **không chứng minh đây là pain phổ biến**. Nó chỉ xác nhận hành vi này có tồn tại trong data pack. Dấu hiệu mạnh hơn về khoảng trống sản phẩm là luồng hiện tại gần như luôn kết thúc sau một câu trả lời, không thu bằng chứng người học đã hiểu và không ghi nhận hiểu lầm.

## Ví dụ nguyên văn

1. “TẠO QUIZ ĐỂ TÔI HIỂU RÕ VÀ ÔN LẠI TOÀN BỘ SLIDE NÀY” — `C0063 / T0849`, trang 9.
2. “dựa vào tài liệu này bạn hãy cho tôi bộ quizz liên quan” — `C0287 / T1113`, trang 47.
3. “vậy prompt engineerig có phải là mô tả lại ngữ cảnh của câu để cho AI hiểu rõ hơn không” — `C0242 / T0720`, trang 4.
4. “benchmark là gì? Mỗi đề bài thì phải tự tạo benchmark đúng không, cho ví dụ” — `C0343 / T0633`, trang 23.
5. “tức là trang này đang nói đến việc nên kiểm định giả thuyết nào, nên kiểm chứng nào chứ ko phải là nên xây dựng sản phẩm nào đúng không” — `C0350 / T0521`, trang 13.
6. “tức là probe cho chúng ta biết chính xác ở layẻ đó model đang suy luận thế nào, và khi can thiệp vào thì nghiên cứu chỉ ra output sẽ bị thay đổi theo nội dung bị can thiệp?” — `C0461 / T0782`, trang 43.
7. “Có phải là một câu hỏi có 4 câu thì transformer sẽ xử lý đồng loạt 4 câu đó thay vì xử lý từng câu đúng k?” — `C0468 / T1015`, trang 22.
8. “tóm tắt những ý chính, chi tiết để tôi có thể làm quiz kahoot cuối giờ” — `C0573 / T0257`, trang 3.

## Liên hệ với prototype trên nhánh `develop`

Prototype hiện thực đúng khoảng trống trên theo vòng:

```text
PDF → Knowledge Units có nguồn → Recall/Explain/Apply
→ rubric cố định → đánh giá correct/missing/incorrect/misconception
→ chọn hoạt động tiếp theo → cập nhật mastery
```

Các artifact kiểm chứng:

- `codebase/docs/00_OVERVIEW.md`
- `codebase/docs/01_BUSINESS_REQUIREMENTS.md`
- `codebase/docs/PROGRESS.md`
- `codebase/tests/`

Đây là bằng chứng build/traceability, không thay thế bằng chứng user. Trước CP5 cần khảo sát hoặc validation với ít nhất 3 người dùng; nếu muốn khẳng định độ phổ biến theo chuẩn khảo sát, cần mẫu ≥20 người ngoài nhóm và ≥50% xác nhận.
