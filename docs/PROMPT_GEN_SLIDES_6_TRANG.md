# Prompt tạo slide 6 trang — Reality Check AI

Sao chép toàn bộ prompt bên dưới vào công cụ tạo slide.

---

Bạn là một **Senior Product Designer + AI Product Storyteller**. Hãy tạo một bộ slide thuyết trình hackathon bằng **tiếng Việt**, đúng **6 trang**, tỷ lệ **16:9**, trình bày trong **5 phút**, dựa hoàn toàn trên dữ liệu được cung cấp dưới đây.

## Nguyên tắc bắt buộc

1. Không tạo slide bìa riêng; slide 1 vừa giới thiệu sản phẩm vừa trình bày User & Job.
2. Không thêm trang phụ, appendix hoặc trang cảm ơn.
3. Mỗi slide phải có ít nhất một con số, quote có mã nguồn, hoặc kết quả đo kiểm chứng được.
4. **Tuyệt đối không bịa** khảo sát, quote validation, golden set, quality bar, tên nhóm, zone hoặc kết quả gọi model thật.
5. Chỗ chưa có dữ liệu phải giữ nguyên nhãn `[CẦN BỔ SUNG: ...]` trong một thẻ màu hổ phách; không tự điền.
6. Nội dung trên slide ngắn, ưu tiên headline kết luận, số lớn, sơ đồ và hình minh họa. Không biến slide thành tài liệu đặc chữ.
7. Mỗi trang phải có speaker notes 3–5 câu, nhưng notes không được tính là nội dung hiển thị.
8. Ghi nguồn nhỏ ở chân trang, ví dụ: `Nguồn: evidence-section1.md — C0063/T0849`.

## Phong cách hình ảnh

- Tinh thần: hiện đại, tin cậy, mang cảm giác “learning analytics”, không dùng phong cách robot/chatbot sáo rỗng.
- Nền xanh navy rất đậm `#071426`, thẻ nội dung xanh than `#10233F`.
- Màu chính cyan `#27D3F2`; màu nhấn lime `#A8F05A`; cảnh báo hổ phách `#FFB547`; lỗi đỏ san hô `#FF6B6B`.
- Chữ trắng ngà `#F5F7FA`; font sans-serif hiện đại như Be Vietnam Pro, Inter hoặc Aptos.
- Dùng lưới rõ ràng, nhiều khoảng thở, góc bo 16–20 px, icon nét mảnh đồng nhất.
- Số liệu chính dùng cỡ chữ rất lớn; tối đa khoảng 35–45 từ hiển thị mỗi slide, không tính nguồn.
- Dùng hình ảnh/sơ đồ liên quan đến “đọc → tự nhớ → giải thích → áp dụng → nhận feedback”, không dùng ảnh stock người bắt tay.
- Có thanh tiến trình nhỏ `01/06` đến `06/06` ở góc dưới.

## Thông tin sản phẩm

- Tên: **Reality Check AI**.
- Track: **Hướng A — VLearn**.
- Loại: **Tính năng mới**.
- Job executor: học viên tự học trên VLearn, vừa đọc xong một đơn vị kiến thức dạng chữ và cần quyết định học tiếp hay ôn lại.
- Core JTBD: **“Kiểm chứng mình có thể nhớ, giải thích và áp dụng một đơn vị kiến thức sau khi đọc để quyết định học tiếp hay ôn lại.”**
- Problem: đọc lại và tự tóm tắt tạo cảm giác quen thuộc nhưng chưa chứng minh hiểu thật; quiz/rubric có thể không ổn định; phản hồi thường không tách rõ đúng, thiếu, sai và misconception.
- Product loop:
  `PDF → Knowledge Units có nguồn → Recall → Explain → Apply → rubric cố định → correct/missing/incorrect/misconception → quyết định tiếp theo → cập nhật mastery`.
- Automation: **conditional**. Workflow và rule xác định điều khiển đường chính; mô hình chỉ xử lý tác vụ ngữ nghĩa; Tutor Agent chỉ chạy cho ngoại lệ đủ điều kiện, có allow-list tool và giới hạn bước.
- Cost of error: đánh giá sai có thể khiến học viên học tiếp quá sớm hoặc ghi nhớ kiến thức sai, nên không giao toàn quyền quyết định mastery cho mô hình.

## Bằng chứng người dùng

- Data pack: 2.522 message, 1.261 lượt hỏi–đáp, 369 học viên, 585 hội thoại; thời gian 22/07–29/07/2026.
- Sau lọc từ khóa và gán nhãn tay: 11/1.261 lượt (0,9%), từ 10/369 học viên (2,7%), chủ động xin quiz hoặc đưa cách hiểu ra để xác nhận.
- Chỉ 3/1.261 câu trả lời tutor (0,24%) chủ động hỏi kiểm tra hiểu.
- 0/1.261 câu trả lời ghi nhận misconception.
- Phải nói rõ: 11 lượt chỉ chứng minh hành vi tồn tại, **không đủ kết luận pain phổ biến**.
- Quote ưu tiên:
  - “TẠO QUIZ ĐỂ TÔI HIỂU RÕ VÀ ÔN LẠI TOÀN BỘ SLIDE NÀY” — `C0063/T0849`, trang 9.
  - “dựa vào tài liệu này bạn hãy cho tôi bộ quizz liên quan” — `C0287/T1113`, trang 47.
  - “tức là trang này đang nói đến việc nên kiểm định giả thuyết nào, nên kiểm chứng nào chứ ko phải là nên xây dựng sản phẩm nào đúng không” — `C0350/T0521`, trang 13.
  - “Có phải là một câu hỏi có 4 câu thì transformer sẽ xử lý đồng loạt 4 câu đó thay vì xử lý từng câu đúng k?” — `C0468/T1015`, trang 22.

## Prototype đã build

- Local modular monolith: Streamlit → FastAPI → Workflow → Service → Rule/Agent → Repository → SQLite.
- Phases 1–5 đã hoàn thành: PDF/Knowledge Map, câu hỏi và rubric, evaluation, adaptive learning/mastery, Tutor Agent giới hạn.
- Câu hỏi gồm Recall, Explain và Apply.
- Reference answer và rubric được tạo, lưu trước khi học viên trả lời và không bị viết lại theo câu trả lời.
- Evaluation tách correct, missing, incorrect và misconception; confidence thấp thì yêu cầu làm rõ.
- Mastery dùng rule bảo thủ; không thể đạt `MASTERED` chỉ từ một câu trả lời.
- Tutor Agent là optional, bounded, allow-listed, có trace; khi tắt agent, luồng học chính vẫn chạy.
- Non-goals/giới hạn: chưa production deployment, chưa auth đa người dùng, chưa OCR PDF scan, xử lý PDF còn đồng bộ, chưa advanced spaced repetition, không multi-agent.

## Kết quả kỹ thuật hiện có

- `pytest -q`: **100 tests passed**, có 1 cảnh báo deprecation không làm fail.
- Pipeline fixture: **3 trang đọc được → 3 Knowledge Units hợp lệ → coverage 100%**.
- `python -m compileall`: passed.
- `python -m pip check`: không có dependency hỏng.
- 10 acceptance scenarios AT-001 đến AT-010 được ghi trạng thái Passed: health, frontend, upload/process PDF, generate questions, phân biệt chất lượng câu trả lời, mastery, agent trigger/step limit/disabled mode.
- Lưu ý: default test dùng fake structured model; hành vi live provider chưa được xác minh.
- Repo có golden set **20 case** tại `adaptive-learning-system/eval/golden_set.json`: 4 Happy Path, 4 Incomplete, 5 Misconception, 4 Hallucination và 3 Low Confidence.
- Quality bar trong `spec.md` §7: **đạt khi ≥90% case được phân loại đúng lỗi thiếu sót/misconception**.
- `spec.md` §7 báo cáo hai lượt: **75% → 100%** sau khi sửa system prompt để tách Correctness/Coverage và điều chỉnh golden set.
- Khi trình bày phải gọi đây là “kết quả được báo cáo trong spec”; không nói có log chạy độc lập nếu repo chưa lưu output log.
- Repo **chưa có** validation log và quote từ user test.

## Nhóm

- Trần Hoàng Quân — 2A202601805 — Bằng chứng.
- Đinh Huy Mạnh — 2A202601677 — Prompt.
- Nguyễn Quang Hưng — 2A202601523 — Build.
- Lê Minh Khiêm — 2A202601645 — Spec.
- Đàm Minh Tuấn — 2A202601169 — Validation.
- Nhóm và Zone chưa được cung cấp: giữ `[XX]` và `[X]`, không tự đoán.

## Cấu trúc chính xác từng slide

### Slide 1 — User & Job, 45 giây

Headline: **“Đọc xong chưa có nghĩa là hiểu thật.”**

- Đặt logo chữ `Reality Check AI` và nhãn `VLearn · Tính năng mới`.
- Hiển thị Core JTBD trong một câu.
- Dùng hai số lớn đối lập: `3/1.261` câu trả lời kiểm tra hiểu và `0/1.261` ghi nhận misconception.
- Đặt quote `C0063/T0849` trong speech bubble.
- Thêm chú thích nhỏ: nhu cầu trực tiếp chỉ 11 lượt, chưa đủ kết luận pain phổ biến.
- Visual: một đường chuyển từ “Đọc” sang “Học tiếp?” bị đứt ở giữa bởi dấu hỏi.

### Slide 2 — Vì sao chọn Reality Check AI, 45 giây

Headline: **“Khoảng trống không phải thiếu câu trả lời — mà thiếu bằng chứng đã hiểu.”**

Tạo bảng impact rút gọn ba ứng viên:

| Ứng viên | Tín hiệu | Khoảng trống | Quyết định |
|---|---:|---|---|
| Flashcard tự sinh từ PDF | Dễ build, dùng hằng ngày | Chỉ kiểm tra Recall | Loại |
| Tutor chat tự do | Dùng hằng ngày | Dễ lạc đề, khó đo mastery | Loại |
| Reality Check thích ứng | 3/1.261 check hiểu; 0 misconception | Recall–Explain–Apply + rubric + mastery | **Chọn** |

- Không tuyên bố Reality Check có nhiều user nhất.
- Nêu rõ lý do chọn là khoảng trống chiến lược + chi phí học sai + prototype khả thi.
- Đặt thẻ cảnh báo: `[CẦN BỔ SUNG: bảng impact chính thức §2 và số người/tần suất cho từng ứng viên]`.

### Slide 3 — Giải pháp & demo live, 2 phút

Headline: **“Một vòng kiểm chứng: Recall → Explain → Apply.”**

- Vẽ product loop theo chiều ngang, tô sáng quyết định trung tâm: `evaluation + rule chọn next action`.
- Một dòng automation: `Conditional — model đánh giá ngữ nghĩa; rule giữ quyền mastery/routing`.
- Một dòng kiến trúc nhỏ: `Streamlit → FastAPI → Workflow → Rules/LLM → SQLite`.
- Chia demo thành hai lane:
  1. **Case chuẩn:** upload PDF 3 trang → tạo 3 Knowledge Units → trả lời → feedback đúng/thiếu/sai → mastery thay đổi.
  2. **Case khó:** câu trả lời chứa misconception lặp lại → rule trigger Tutor Agent giới hạn; tắt agent thì dùng remediation xác định.
- Hiển thị badge: `Rubric được khóa trước khi user trả lời`.
- Speaker notes phải ghi chính xác thao tác bấm demo trong 2 phút và nhắc không dùng video nếu live chạy được.

### Slide 4 — Kết quả đo, 45 giây

Headline: **“20 case: từ 75% lên 100%, vượt quality bar 90%.”**

- Biểu đồ chính: hai cột `Lần 1: 75%` và `Lần 2: 100%`, thêm đường quality bar `90%`.
- Ghi cơ cấu golden set bằng năm chip: `4 Happy`, `4 Incomplete`, `5 Misconception`, `4 Hallucination`, `3 Low Confidence`.
- Failure đáng kể nhất của lần 1: evaluator trừ Correctness quá ngặt với câu trả lời Incomplete và không xuất misconception cho một số lỗi ảo giác.
- Thay đổi: sửa system prompt để tách Correctness khỏi Coverage; spec cũng ghi đã nới golden set, vì vậy phải nêu đây là rủi ro “test-set tuning” cần khóa lại ở vòng sau.
- Thêm hàng bằng chứng kỹ thuật nhỏ: `100 tests passed · 3/3 KU · 100% source coverage`.
- Hiển thị giới hạn: kết quả 75%/100% được báo cáo trong spec; default test dùng fake model và repo chưa có output log độc lập của lượt eval.
- Không biến “100 tests passed” thành “100% chất lượng AI”.

### Slide 5 — User thật nói gì, 45 giây

Headline tạm: **“Validation phải quyết định điều gì?”**

- Tuyệt đối không dùng quote từ chatlog mining như quote validation.
- Vì repo chưa có validation, tạo layout sẵn gồm hai quote card:
  - `[CẦN BỔ SUNG: quote nguyên văn user 1 — tên/vai]`
  - `[CẦN BỔ SUNG: quote nguyên văn user 2 — tên/vai]`
- Tạo ba metric card cần điền: `thời gian hoàn thành 1 vòng`, `% hiểu được feedback 4 nhóm`, `% đồng ý với next action`.
- Khung “Đã thay đổi sau feedback”: `[CẦN BỔ SUNG: thay đổi + feedback ID]`.
- Ghi nhỏ: `Owner validation: Đàm Minh Tuấn · yêu cầu ≥5 feedback log có tên`.
- Slide phải trông hoàn chỉnh về layout nhưng thể hiện trung thực trạng thái “pending”, không giả lập lời khen.

### Slide 6 — Nếu có thêm 1 tuần, 30 giây

Headline: **“Từ prototype chạy được → bằng chứng học tốt hơn.”**

Chỉ trình bày ba ưu tiên theo thứ tự:

1. **Khóa eval v2:** không chỉnh expected range sau khi chạy; lưu output log, thêm ≥10 case từ chatlog và chạy live provider.
2. **Validate với người học:** ≥5 feedback có tên; đo thời gian, độ rõ feedback và mức tin cậy vào next action.
3. **Hardening demo:** xử lý bất đồng bộ, error/logging review, kiểm tra cross-platform; OCR vẫn là non-goal nếu không đủ thời gian.

- Bài học lớn nhất: **“Đừng đo hiểu bài bằng việc đã đọc xong; hãy đo bằng bằng chứng người học tạo ra.”**
- Footer nhỏ hiển thị phân công 5 thành viên theo vai trò.
- Kết bằng câu nói, không thêm slide cảm ơn: **“Reality Check AI biến ‘mình nghĩ là hiểu’ thành ‘mình chứng minh được là hiểu’.”**

## Yêu cầu đầu ra

1. Xuất đúng 6 slide hoàn chỉnh.
2. Với mỗi slide, cung cấp:
   - tiêu đề;
   - nội dung hiển thị;
   - bố cục/visual cụ thể;
   - speaker notes;
   - nguồn ở footer.
3. Nếu công cụ hỗ trợ, xuất file `.pptx` và PDF với font được embed.
4. Kiểm tra lần cuối:
   - không có số liệu ngoài dữ liệu đầu vào;
   - không có quote validation giả;
   - không nhầm test kỹ thuật với golden-set quality;
   - không vượt quá 6 slide;
   - tổng thời lượng notes bằng khoảng 5 phút.
