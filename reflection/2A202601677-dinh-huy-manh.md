# Reflection — Đinh Huy Mạnh

- **Mã học viên:** 2A202601677
- **Vai trò chính:** Slide

## Tôi đã làm gì?

Tôi phụ trách chuyển nội dung kỹ thuật và sản phẩm của nhóm thành câu chuyện trình bày ngắn gọn. Tôi đã rà soát `spec.md`, phần evidence/JTBD và prototype để xác định những thông tin quan trọng cần xuất hiện trong bài trình bày: vấn đề của người học, bằng chứng, lát cắt sản phẩm, cách hệ thống đánh giá câu trả lời và giá trị của vòng Active Recall thích ứng.

Khi xây dựng hướng nội dung cho slide, tôi ưu tiên một mạch kể sáu phần: pain của người học, evidence, quyết định chọn giải pháp, trải nghiệm chính, cách hệ thống kiểm soát lỗi và kết quả kiểm thử. Tôi cũng phối hợp với các phần Spec, Evidence và Build để hạn chế việc slide đưa ra tuyên bố mạnh hơn dữ liệu mà nhóm đang có.

## Quyết định quan trọng nhất

Quyết định quan trọng nhất của tôi là không biến slide thành bản sao rút gọn của toàn bộ spec. Với thời lượng demo ngắn, tôi chọn tập trung vào một thông điệp: người học không chỉ cần đọc lại tài liệu mà cần tự đưa kiến thức ra, nhận phản hồi có căn cứ và biết nên học tiếp hay ôn lại.

Tôi cũng quyết định trình bày rõ giới hạn của bằng chứng thay vì che giấu chúng. Những tỷ lệ hoặc kết quả kiểm thử chỉ nên xuất hiện khi có thể truy ngược về dữ liệu và cách đo trong repo. Điều này giúp câu chuyện thuyết phục hơn và giảm rủi ro bị phản biện vì số liệu thiếu căn cứ.

## Tôi học được gì?

Tôi học được rằng slide cho sản phẩm AI không chỉ cần đẹp mà phải thể hiện được logic ra quyết định. Một bản trình bày tốt cần nối liền:

1. người dùng và công việc họ cần hoàn thành;
2. bằng chứng cho thấy vấn đề thực sự tồn tại;
3. lý do chọn lát cắt này thay vì các phương án khác;
4. phần AI quyết định và phần rule kiểm soát;
5. cách nhóm kiểm thử chất lượng và xử lý khi AI không chắc chắn.

Tôi cũng nhận ra tính nhất quán giữa slide, spec và prototype quan trọng hơn số lượng hiệu ứng. Nếu tên sản phẩm, job executor, evidence hoặc phân công khác nhau giữa các artifact, người nghe sẽ khó tin vào phần demo dù giao diện được trình bày tốt.

## Nếu làm lại, tôi sẽ làm gì khác?

Nếu làm lại, tôi sẽ chốt thông điệp và cấu trúc slide ngay sau khi nhóm khóa §1–§4, sau đó cập nhật dần theo changelog thay vì đợi gần buổi demo mới tổng hợp. Tôi cũng sẽ:

- tạo sớm một bản slide ít chữ để thử thời lượng trình bày;
- yêu cầu mỗi số liệu trên slide có đường dẫn tới evidence tương ứng;
- lấy ảnh thật từ prototype thay cho mockup khi luồng chính đã ổn định;
- tập demo với ít nhất ba người ngoài nhóm và ghi lại câu hỏi họ chưa hiểu;
- chuẩn bị phương án dự phòng nếu API hoặc kết nối mạng lỗi trong lúc trình bày.

## Đóng góp tôi có thể giải thích khi được hỏi

Tôi có thể giải thích cách chọn nội dung cho sáu trang, lý do ưu tiên mạch kể theo user pain → evidence → solution → demo → safety/evaluation → call to action, và cách kiểm tra để các tuyên bố trên slide không mâu thuẫn với `spec.md` hoặc prototype.
