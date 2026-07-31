# Nói Lại Đi — VLearn UI + Adaptive Learning backend

Giao diện prototype VLearn này hiện đã kết nối với backend trong
`adaptive-learning-system`.

## Chạy

Khởi động backend:

```powershell
cd adaptive-learning-system
.\.venv\Scripts\python.exe scripts\run_backend.py
```

Mở:

```text
http://127.0.0.1:8000/vlearn/
```

Backend phục vụ trực tiếp HTML, CSS và JavaScript nên không cần chạy thêm web
server. Khi phát triển riêng frontend, vẫn có thể chạy port `8899`; backend chỉ
cho phép các origin local đã khai báo, không bật wildcard CORS.

## Luồng thật

1. Vào **Khóa học của tôi → Mở khóa học**.
2. Chọn hoặc kéo-thả một PDF có text.
3. UI tự upload PDF, gọi process và mở reader khi Knowledge Map hoàn tất.
4. Sidebar bên trái hiển thị các Knowledge Unit cùng phạm vi slide nguồn.
5. Chọn KU để mở đúng slide, lesson và câu hỏi đầu tiên ở panel bên phải.
6. Gửi câu trả lời để nhận các ý đúng, thiếu, chưa đúng, hiểu lầm và mastery.
7. Câu hỏi tiếp theo được nạp từ cùng learning session; đổi KU sẽ chuẩn bị
   learning session tương ứng.

## Phân chia trách nhiệm

| Thành phần | Nguồn dữ liệu |
|---|---|
| Điều hướng, reader, màu sắc, typography | `index.html` và `backend-integration.css` |
| Gọi upload/process/session/question/answer | `backend-integration.js` |
| PDF đang hiển thị | Blob tạm trong bộ nhớ trình duyệt |
| Tài liệu, KU, câu hỏi, session, mastery | FastAPI + SQLite hiện có |
| Knowledge Map, rubric và feedback | Pipeline LLM hiện có |

Nội dung từ backend được escape trước khi đưa vào HTML. API key không xuất hiện
trong frontend; mọi lời gọi provider vẫn đi qua backend.

## Demo cũ

Các slide và logic rule-based ban đầu vẫn được giữ để đối chiếu thiết kế. Luồng
backend thật bắt đầu khi người dùng chọn PDF. Đây vẫn là prototype, không phải
VLearn chính thức.
