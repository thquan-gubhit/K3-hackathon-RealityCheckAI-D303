# Reflection — Đinh Huy Mạnh

- **Mã học viên:** 2A202601677
- **Vai trò chính:** Prompt

## Tôi đã làm gì?

Tôi phụ trách phần prompt cho hệ thống học tập thích ứng. Công việc của tôi không chỉ là viết một câu lệnh cho mô hình mà là chuyển yêu cầu trong `spec.md` thành những chỉ dẫn có đầu vào, đầu ra và giới hạn rõ ràng để tích hợp được với workflow.

Tôi tập trung vào các nhóm prompt chính:

- tách tài liệu thành các Knowledge Unit có mục tiêu học độc lập;
- sinh câu hỏi theo ba mức Recall, Explain và Apply;
- sinh reference answer và rubric trước khi nhận câu trả lời của người học;
- đánh giá câu trả lời theo bốn chiều Correctness, Coverage, Reasoning và Application;
- phát hiện misconception, nội dung không có căn cứ và câu trả lời quá mơ hồ;
- tạo feedback giúp người học biết phần nào đúng, thiếu hoặc sai và nên làm gì tiếp theo.

Tôi phối hợp với phần Build để output của mô hình tuân theo schema có cấu trúc, có thể kiểm tra bằng Pydantic và được workflow sử dụng ổn định. Prompt không được tự quyết định toàn bộ luồng học: mô hình xử lý phần ngữ nghĩa, còn Rule Engine kiểm soát việc cập nhật mastery, chuyển câu hỏi hoặc kích hoạt remediation.

Tôi cũng rà soát prompt theo các case trong Golden Set. Qua các lượt thử, nhóm nhận thấy Evaluator từng trừ điểm Correctness quá mạnh với câu trả lời chưa đầy đủ và đôi lúc không phát hiện misconception. Hướng điều chỉnh là tách rõ Correctness khỏi Coverage, yêu cầu mô hình chỉ kết luận từ source context và trả về các trường đánh giá riêng thay vì một nhận xét chung.

## Quyết định quan trọng nhất

Quyết định quan trọng nhất của tôi là yêu cầu sinh rubric và reference answer trước khi người học trả lời. Nếu rubric được tạo sau khi đã nhìn thấy câu trả lời, mô hình có thể thay đổi tiêu chí để hợp thức hóa hoặc phạt câu trả lời một cách thiếu nhất quán.

Tôi cũng chọn structured output thay cho văn bản tự do. Mỗi kết quả cần có điểm theo từng chiều, confidence, detected misconceptions và feedback. Cách này giúp code kiểm tra được output, xử lý lỗi rõ ràng và không phụ thuộc vào việc phân tích một đoạn văn do mô hình sinh ra.

## Cách tôi kiểm soát lỗi của AI

- **Không có căn cứ:** yêu cầu đánh giá chỉ dựa trên source context, reference answer và rubric.
- **Thiếu thông tin:** hạ confidence và yêu cầu người học giải thích rõ hơn thay vì tự suy diễn.
- **Ngoài phạm vi:** không chấm kiến thức không xuất hiện trong tài liệu như thể đó là đáp án chuẩn.
- **Misconception:** tách lỗi sai bản chất khỏi câu trả lời chỉ thiếu ý để workflow chọn remediation phù hợp.
- **Output sai cấu trúc:** schema validation chặn kết quả không hợp lệ trước khi cập nhật mastery.
- **Lộ đáp án:** prompt sinh câu hỏi phải giữ reference answer và rubric ở phía hệ thống, không đưa chúng vào câu hỏi cho người học.

## Tôi học được gì?

Tôi học được rằng chất lượng prompt không nên được đánh giá bằng cảm giác “câu trả lời nghe hay”. Prompt tốt phải tạo ra hành vi có thể kiểm chứng trên nhiều trường hợp, đặc biệt là các trường hợp khó như câu trả lời ngắn, đúng một phần, bịa kiến thức hoặc diễn đạt khác reference answer nhưng vẫn hợp lý.

Tôi cũng hiểu rõ hơn ranh giới giữa LLM và rule. LLM phù hợp với việc hiểu ngữ nghĩa và tạo phản hồi, nhưng các quyết định có ảnh hưởng đến trạng thái học tập cần có ngưỡng, schema và rule rõ ràng. Khi cost-of-error cao hoặc confidence thấp, hệ thống nên dừng và hỏi lại thay vì tự động kết luận.

## Nếu làm lại, tôi sẽ làm gì khác?

Nếu làm lại, tôi sẽ quản lý prompt như một artifact có phiên bản ngay từ đầu. Mỗi lần thay đổi cần ghi:

1. case nào đang thất bại;
2. giả thuyết về nguyên nhân;
3. phần prompt được sửa;
4. kết quả trước và sau trên cùng Golden Set;
5. lỗi hồi quy xuất hiện ở case khác.

Tôi cũng sẽ bổ sung nhiều case lấy trực tiếp từ chatlog hoặc user validation, lưu log chạy độc lập thay vì chỉ ghi tỷ lệ trong spec, và thử prompt trên nhiều cách diễn đạt tiếng Việt để tránh tối ưu quá mức cho một bộ câu trả lời mẫu.

## Đóng góp tôi có thể giải thích khi được hỏi

Tôi có thể giải thích cấu trúc prompt cho từng bước, lý do tách Correctness và Coverage, cách rubric sinh trước giảm thiên lệch, cách structured output kết nối với Pydantic và Rule Engine, cũng như cách dùng Golden Set để phát hiện và sửa lỗi prompt.
