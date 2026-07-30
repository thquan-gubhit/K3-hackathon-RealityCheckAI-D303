# Nói Lại Đi — prototype (Sketch/Mock)

Prototype một tính năng cho VLearn: **động từ thứ tư trên menu bôi đen**.

Hiện VLearn cho học viên ba lựa chọn khi bôi đen một đoạn slide — `Hỏi AI` · `Báo bối rối` ·
`Ghi chú` — và bảy công cụ đánh dấu (Đọc, Bút, Highlight, Khoanh, Text, Ảnh, Tẩy).
Tất cả đều giữ học viên ở thế **nhận vào**. Không có động từ nào bắt học viên **nói ra**.

`Nói lại` là động từ đó.

## Chạy

```bash
python -m http.server 8899
```

rồi vào `http://127.0.0.1:8899/` (chạy lệnh trong đúng thư mục này).

Không `npm install`, không build, không cần mạng, không cần API key.

> **Phải chạy qua http, đừng bấm đúp file.** Tính năng đọc slide upload dùng
> PDF.js (`vendor/`) để vẽ **từng trang một** ra canvas — worker của nó bị trình
> duyệt chặn khi mở bằng `file://`. Các phần khác vẫn chạy với `file://`, riêng
> phần xem PDF thì không.

`vendor/pdf.min.js` + `vendor/pdf.worker.min.js` là pdfjs-dist 3.11 (Apache-2.0),
để sẵn trong repo nên chạy offline được.

## Nối backend — khi nào cần

FE hiện chạy **độc lập hoàn toàn**, chấm bằng luật (`grade()`).
Chỗ nối đã chừa sẵn ở đầu phần `<script>`:

```js
const API = { base: null, sessionId: null };   // null = chạy offline
```

Đổi `base` thành `'http://127.0.0.1:8000'` là FE gọi thẳng `adaptive-learning-system`.
Hàm `evaluate()` đã khớp sẵn hợp đồng của backend:

```
POST /learning-sessions/{id}/answers   { question_id, user_answer }
  -> { evaluation: { correct_points[], missing_points[], feedback, ... } }
```

Nếu backend không phản hồi, `evaluate()` **tự quay về chấm offline** — demo không bao giờ vỡ.
Không phải sửa chỗ nào khác trong file.

## Luồng demo

1. Vào **Khóa học của tôi → Mở khóa học → Day01 → `day01_302.pdf`**.
2. Cuộn tới **trang 32 (Attention)** — hoặc trang 30 (Token).
3. **Bôi đen** một ý trong danh sách → menu nổi hiện 4 nút → bấm **Nói lại**.
4. Đoạn vừa bôi đen **mờ đi tại chỗ** (chỉ đoạn đó, không chặn cả trang), panel bên phải
   chuyển sang một câu hỏi tình huống + ô trống.
5. Gõ bằng lời của mình → nhận phản hồi ba phần: *đã nắm* / *chưa nhắc tới* / *chỗ tài liệu nói ý này*.
6. Kết quả ghim vào note của trang → xem tổng hợp ở **Sổ tay học tập**.

### Hai câu để thử tại chỗ

| Gõ vào | Kết quả mong đợi |
|---|---|
| `Đây là cơ chế attention, có vector Q K V, multi-head rồi softmax chuẩn hoá.` | Bị chỉ ra: gọi đúng tên thành phần nhưng **chưa nói chúng làm gì** |
| `Bình thường máy đọc chữ nào biết chữ đó thôi. Cái này thì mỗi chữ được ngó lại mấy chữ đứng trước nó, rồi tự cân xem chữ nào dính tới mình nhiều nhất...` | **Đủ ý** — diễn đạt khác tài liệu nhưng đúng bản chất |

Hai câu cạnh nhau chứng minh hệ thống **đo hiểu, không đo từ vựng**.

## Quyết định trung tâm của AI

Không phải "chấm điểm độ hiểu" (chủ quan, không có đáp án đúng để so).
Mà là: **so câu trả lời của học viên với danh sách "ý bắt buộc" của đoạn nguồn — ý nào có, ý nào thiếu.**

Mỗi ý bắt buộc trace được về một câu có thật trong slide (`data-src`), nên người thứ hai mở
đoạn nguồn ra là chấm lại được cùng kết quả.

## Trạng thái hiện tại

| Phần | Mức |
|---|---|
| Giao diện reader / khoá học / sổ tay | dựng lại theo VLearn thật |
| Nội dung slide | **thật**, trích từ `day01_302.pdf` trang 30–32 và `Day03-D302…pdf` trang 7–9 |
| Thẻ ý bắt buộc | 3 thẻ: `d01a:30` (Token), `d01a:32` (Attention), `d03b:8` (Agent vs Chatbot) |
| Chấm | **rule-based** (`grade()`) — chưa nối LLM |
| Các tài liệu khác | mở được, đúng tên/mã/số trang, nhưng chưa dựng nội dung |

**Việc tiếp theo:** thay `grade()` bằng một lời gọi LLM thật ở đúng quyết định trung tâm,
giữ bản rule-based làm fallback khi mất mạng. Log/trace lưu trong repo.

## Lưu ý

- Đây **không phải** VLearn thật — có nhãn `PROTOTYPE` cố định ở góc màn hình.
- Nội dung slide chỉ trích phần tối thiểu để minh hoạ. Tài liệu khoá học theo chính sách
  **chỉ xem online**, không phát tán.
- Không chứa thông tin cá nhân, không chứa API key.
