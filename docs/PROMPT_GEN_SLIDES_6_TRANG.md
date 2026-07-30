# Prompt tạo slide 6 trang — Reality Check AI

Sao chép toàn bộ prompt bên dưới vào công cụ tạo slide.

---

Bạn là một **Senior Product Designer + AI Product Storyteller**. Hãy tạo một bộ slide thuyết trình hackathon bằng **tiếng Việt**, đúng **6 trang**, tỷ lệ **16:9**, trình bày trong **5 phút**, dựa hoàn toàn trên dữ liệu được cung cấp dưới đây.

## Thứ tự ưu tiên thông tin

Khi tổng hợp nội dung, dùng thứ tự sau:

1. `spec.md` §1 là nguồn chính thức cho User, Workflow, Core JTBD, Problem statement và evidence khảo sát.
2. `spec.md` §2–§9 là nguồn chính thức cho impact, thiết kế, failure taxonomy, golden set, quality bar và kết quả các lượt eval.
3. `adaptive-learning-system/` cùng tài liệu kiến trúc/test là nguồn chứng minh những phần đã build và hành vi kỹ thuật.
4. `adaptive-learning-system/README.md` và `TEAMMATE.md` là nguồn cho tên, mã học viên và phân công hiện tại.
5. Không lấy persona, track hoặc evidence từ các tài liệu §1 cũ để thay thế §1 hiện tại trong `spec.md`.

## Nguyên tắc bắt buộc

1. Không tạo slide bìa riêng; slide 1 vừa giới thiệu sản phẩm vừa trình bày User & Job.
2. Không thêm trang phụ, appendix hoặc trang cảm ơn.
3. Mỗi slide phải có ít nhất một con số, quote có mã nguồn, hoặc kết quả đo kiểm chứng được.
4. **Tuyệt đối không bịa** khảo sát, quote validation, golden set, quality bar, tên nhóm, zone hoặc kết quả gọi model thật.
5. Chỗ chưa có dữ liệu phải giữ nguyên nhãn `[CẦN BỔ SUNG: ...]` trong một thẻ màu hổ phách; không tự điền.
6. Nội dung trên slide ngắn, ưu tiên headline kết luận, số lớn, sơ đồ và hình minh họa. Không biến slide thành tài liệu đặc chữ.
7. Mỗi trang phải có speaker notes 3–5 câu, nhưng notes không được tính là nội dung hiển thị.
8. Ghi nguồn nhỏ ở chân trang, ví dụ: `Nguồn: spec.md §1 · khảo sát n=17`.

## Phong cách hình ảnh

- Tinh thần: **premium AI product pitch**, hiện đại, tin cậy, mang cảm giác “learning analytics”, không dùng phong cách robot/chatbot sáo rỗng.
- Nền xanh navy rất đậm `#071426`, thẻ nội dung xanh than `#10233F`.
- Màu chính cyan `#27D3F2`; màu nhấn lime `#A8F05A`; cảnh báo hổ phách `#FFB547`; lỗi đỏ san hô `#FF6B6B`.
- Chữ trắng ngà `#F5F7FA`; font sans-serif hiện đại như Be Vietnam Pro, Inter hoặc Aptos.
- Dùng lưới rõ ràng, nhiều khoảng thở, góc bo 16–20 px, icon nét mảnh đồng nhất, đổ bóng mềm và viền phát sáng rất nhẹ.
- Số liệu chính dùng cỡ chữ rất lớn; tối đa khoảng 30–40 từ hiển thị mỗi slide, không tính nguồn.
- Mỗi slide chỉ có **một điểm nhìn chính**: một con số, một sơ đồ hoặc một insight; không chia thành quá nhiều ô nhỏ.
- Dùng hình minh họa bán trừu tượng liên quan đến “đọc → tự nhớ → giải thích → áp dụng → nhận feedback”, không dùng ảnh stock người bắt tay, robot hoặc não phát sáng sáo rỗng.
- Có thể dùng các dải gradient cyan–violet, đường kết nối dạng node, vòng tròn mastery và texture lưới mờ để tạo chiều sâu.
- Có thanh tiến trình nhỏ `01/06` đến `06/06` ở góc dưới.

## Motion design và hiệu ứng trình chiếu

- Dùng transition **Morph** hoặc **Fade Through Black** xuyên suốt để deck có cảm giác liền mạch.
- Mỗi slide chỉ dùng 2–4 animation có chủ đích; không dùng hiệu ứng xoay, bounce, âm thanh hoặc chữ bay ngẫu nhiên.
- Reveal nội dung theo đúng nhịp lời nói; không hiện toàn bộ slide ngay từ đầu.
- Con số chính dùng animation count-up hoặc scale nhẹ trong 0,4–0,6 giây.
- Sơ đồ workflow dùng line-draw/progressive reveal từ trái sang phải.
- Card xuất hiện bằng fade + rise 12–20 px; độ trễ giữa các card khoảng 0,15 giây.
- Highlight quyết định quan trọng bằng glow/pulse một lần, không lặp vô hạn.
- Chuyển từ slide 1→2 bằng cách biến dấu hỏi thành bảng lựa chọn; slide 2→3 biến ứng viên được chọn thành workflow sản phẩm; slide 3→4 biến output evaluation thành biểu đồ kết quả.
- Tất cả animation phải chạy tự nhiên khi người thuyết trình click; không auto-play quá nhanh.

## Nhịp kể chuyện

- Mở bằng tension: **“Bạn vừa đọc xong. Nhưng bạn có thực sự giải thích lại được không?”**
- Mỗi slide phải có một câu takeaway ngắn để người nghe nhớ được ngay cả khi bỏ qua chi tiết.
- Dùng cấu trúc: **Pain → Quyết định → Trải nghiệm → Bằng chứng → Con người → Tương lai**.
- Speaker notes phải có một câu chuyển tiếp sang slide tiếp theo, tránh cảm giác sáu trang rời rạc.
- Ưu tiên động từ và câu nói trực tiếp; tránh thuật ngữ kỹ thuật nếu không phục vụ quyết định sản phẩm.

## Thông tin sản phẩm

- Tên: **Reality Check AI**.
- Track: **Hướng C — Làn mở**.
- Loại: **Tính năng mới**.
- Job executor: học viên tự học vừa đọc xong một tài liệu PDF dài/phức tạp.
- Workflow hiện tại: đọc tài liệu → tóm tắt ý chính → cố gắng nhớ lại/giải thích → tự kiểm tra mình hiểu đúng hay sai.
- Core JTBD: **“Tự kiểm chứng mức độ hiểu và khả năng giải thích một văn bản dài ngay sau khi đọc xong để tránh ảo giác hiểu biết.”**
- Problem: người học thường đọc lại hoặc đưa nội dung vào chatbot để tạo câu hỏi. Đọc lại tạo cảm giác quen thuộc nhưng ít kiểm chứng retrieval; chatbot có thể hallucinate, cho feedback tổng quát và không chấm ổn định theo rubric riêng của tài liệu.
- Product loop:
  `PDF → Knowledge Units có nguồn → Recall → Explain → Apply → rubric cố định → correct/missing/incorrect/misconception → quyết định tiếp theo → cập nhật mastery`.
- Automation: **conditional**. Workflow và rule xác định điều khiển đường chính; mô hình chỉ xử lý tác vụ ngữ nghĩa; Tutor Agent chỉ chạy cho ngoại lệ đủ điều kiện, có allow-list tool và giới hạn bước.
- Cost of error: đánh giá sai có thể khiến học viên học tiếp quá sớm hoặc ghi nhớ kiến thức sai, nên không giao toàn quyền quyết định mastery cho mô hình.

## Bằng chứng người dùng và nghiên cứu

- Khảo sát được ghi trong `spec.md` §1: `n=17`.
- Tình trạng “đọc hiểu ngay nhưng lúc thi hoặc làm bài tập thì không biết giải thích từ đâu”:
  - 23,5% rất thường xuyên;
  - 47,1% thường xuyên;
  - 29,4% thỉnh thoảng.
- Suy ra **70,6%** trả lời “thường xuyên” hoặc “rất thường xuyên”.
- Dùng `n=17` và ba tỷ lệ trên làm evidence chính thức của bài. Ghi cỡ mẫu `n=17` ngay cạnh biểu đồ để người xem hiểu phạm vi bằng chứng.
- Nghiên cứu được liệt kê trong spec:
  - Callender & McDaniel (2009): rereading thường được dùng nhưng phần lớn không làm tăng performance đáng kể.
  - Weinstein, McDermott & Roediger (2010): trả lời câu hỏi và tự sinh câu hỏi có lợi hơn rereading.
  - Wiklund-Hörnqvist & Jonsson (2014): repeated testing có feedback tăng learning so với rereading.
  - Hui et al. (2021): testing effect giúp retention tốt hơn restudying.
  - Bang et al. (2023) và Ji et al. (2022): LLM/NLG có rủi ro hallucination.
  - Nghiên cứu *Computers & Education: AI* (2026): feedback có thể đầy đủ nhưng phức tạp và generic.
- Chỉ dùng trích dẫn rất ngắn trên slide; phần còn lại diễn giải và đặt nguồn ở footer.

## Giải pháp tương tự

- **NotebookLM:** học cách grounding và citation theo trang; tránh luồng thụ động chỉ chờ người dùng hỏi.
- **Khanmigo:** học cách gợi mở Socratic; tránh hỏi ngược quá nhiều khi người học đang hổng kiến thức.
- Reality Check AI khác biệt bằng Knowledge Unit, câu hỏi Recall–Explain–Apply, rubric sinh trước, feedback đa chiều, mastery và remediation có kiểm soát.

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
- Dùng phân công này theo `adaptive-learning-system/README.md` và `TEAMMATE.md`.
- Nhóm và Zone chưa được cung cấp: giữ `[XX]` và `[X]`, không tự đoán.

## Cấu trúc chính xác từng slide

### Slide 1 — User & Job, 45 giây

Headline: **“Đọc xong chưa có nghĩa là hiểu thật.”**

- Đặt logo chữ `Reality Check AI` và nhãn `Làn mở · Tính năng mới`.
- Hiển thị Core JTBD trong một câu.
- Dùng số lớn `70,6%` thường xuyên/rất thường xuyên gặp tình trạng đọc hiểu nhưng không biết giải thích khi thi/làm bài.
- Đặt breakdown nhỏ: `23,5% rất thường xuyên · 47,1% thường xuyên · 29,4% thỉnh thoảng`.
- Ghi rõ ngay cạnh biểu đồ: `Khảo sát n=17`.
- Đặt một trích dẫn nghiên cứu ngắn về testing effect/rereading, không quá 12 từ, kèm tác giả/năm.
- Visual: một đường chuyển từ “Đọc” sang “Học tiếp?” bị đứt ở giữa bởi dấu hỏi.
- Hiệu ứng: mở bằng trang PDF rõ nét rồi làm mờ dần; dấu hỏi xuất hiện; số `70,6%` count-up và trở thành điểm nhìn chính.
- Câu chuyển: **“Nếu đọc lại chưa đủ, nhóm phải chọn cách kiểm chứng nào?”**
- Footer: `Nguồn: spec.md §1 · khảo sát n=17 · Callender & McDaniel (2009)`.

### Slide 2 — Vì sao chọn Reality Check AI, 45 giây

Headline: **“Khoảng trống không phải thiếu câu trả lời — mà thiếu bằng chứng đã hiểu.”**

Tạo bảng impact rút gọn ba ứng viên:

| Ứng viên | Số người | Tần suất | Chi phí/giới hạn | Quyết định |
|---|---:|---|---|---|
| Flashcard tự sinh từ PDF | Chưa đo riêng | Giả thuyết: hàng ngày | Chỉ kiểm tra Recall | Loại |
| Tutor chat tự do | Chưa đo riêng | Giả thuyết: hàng ngày | Dễ lạc đề, khó đo mastery | Loại |
| Reality Check thích ứng | Pain chung: 12/17 | Sau mỗi đơn vị học | Cần rubric + rule + mastery | **Chọn** |

- Nêu lý do chọn: kiểm tra được Recall–Explain–Apply, feedback có căn cứ, quyết định mastery được rule kiểm soát.
- Thêm dải so sánh nhỏ: `NotebookLM = grounding tốt nhưng thụ động` · `Khanmigo = Socratic tốt nhưng có thể hỏi ngược quá nhiều`.
- Đặt thẻ cảnh báo: `[CẦN VALIDATE: khảo sát hiện đo pain chung, chưa đo preference giữa ba ứng viên]`.
- Hiệu ứng: ba ứng viên reveal lần lượt; hai ứng viên bị loại giảm opacity; Reality Check phóng nhẹ và nối bằng một đường sáng sang slide 3.
- Câu chuyển: **“Ứng viên được chọn không chỉ tạo câu hỏi—nó khép kín cả vòng học.”**
- Footer: `Nguồn: spec.md §2–§3`.

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
- Hiệu ứng: workflow chạy progressive reveal; khi đến evaluation, tách câu trả lời thành bốn chip `đúng / thiếu / sai / misconception`; mastery ring tăng bằng animation ngắn.
- Dùng mockup laptop hoặc browser frame lớn ở trung tâm để phần demo trông như sản phẩm thật, không dùng screenshot nhỏ khó đọc.
- Câu chuyển: **“Vòng học chạy được; câu hỏi tiếp theo là nó phân loại có đủ chính xác không.”**
- Footer: `Nguồn: spec.md §4–§6 · adaptive-learning-system/docs/06_WORKFLOWS.md`.

### Slide 4 — Kết quả đo, 45 giây

Headline: **“20 case: từ 75% lên 100%, vượt quality bar 90%.”**

- Biểu đồ chính: hai cột `Lần 1: 75%` và `Lần 2: 100%`, thêm đường quality bar `90%`.
- Ghi cơ cấu golden set bằng năm chip: `4 Happy`, `4 Incomplete`, `5 Misconception`, `4 Hallucination`, `3 Low Confidence`.
- Failure đáng kể nhất của lần 1: evaluator trừ Correctness quá ngặt với câu trả lời Incomplete và không xuất misconception cho một số lỗi ảo giác.
- Thay đổi: sửa system prompt để tách Correctness khỏi Coverage; spec cũng ghi đã nới golden set, vì vậy phải nêu đây là rủi ro “test-set tuning” cần khóa lại ở vòng sau.
- Thêm hàng bằng chứng kỹ thuật nhỏ: `100 tests passed · 3/3 KU · 100% source coverage`.
- Hiển thị giới hạn: kết quả 75%/100% được báo cáo trong spec; default test dùng fake model và repo chưa có output log độc lập của lượt eval.
- Không biến “100 tests passed” thành “100% chất lượng AI”.
- Hiệu ứng: cột `75%` mọc trước, đường quality bar `90%` được vẽ ngang, sau đó cột `100%` vượt qua bar và phát sáng một lần; failure card xuất hiện cuối để giữ tính trung thực.
- Câu chuyển: **“Điểm số tốt chưa đủ—người học thật phải thấy feedback hữu ích.”**
- Footer: `Nguồn: spec.md §7 · eval/golden_set.json · docs/PROGRESS.md`.

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
- Hiệu ứng: hai quote card hiện dưới dạng khung trống có shimmer nhẹ; ba metric card reveal theo câu hỏi validation; tuyệt đối không tạo avatar hoặc tên người dùng giả.
- Câu chuyển: **“Đây là khoảng trống quan trọng nhất mà một tuần tiếp theo phải đóng lại.”**
- Footer: `Nguồn: trạng thái repo Manh — chưa có validation/`.

### Slide 6 — Nếu có thêm 1 tuần, 30 giây

Headline: **“Từ prototype chạy được → bằng chứng học tốt hơn.”**

Chỉ trình bày ba ưu tiên theo thứ tự:

1. **Khóa eval v2:** không chỉnh expected range sau khi chạy; lưu output log, thêm ≥10 case từ chatlog và chạy live provider.
2. **Validate với người học:** ≥5 feedback có tên; đo thời gian, độ rõ feedback và mức tin cậy vào next action.
3. **Hardening demo:** xử lý bất đồng bộ, error/logging review, kiểm tra cross-platform; OCR vẫn là non-goal nếu không đủ thời gian.

- Bài học lớn nhất: **“Đừng đo hiểu bài bằng việc đã đọc xong; hãy đo bằng bằng chứng người học tạo ra.”**
- Footer nhỏ hiển thị phân công 5 thành viên theo vai trò.
- Kết bằng câu nói, không thêm slide cảm ơn: **“Reality Check AI biến ‘mình nghĩ là hiểu’ thành ‘mình chứng minh được là hiểu’.”**
- Hiệu ứng: ba ưu tiên xuất hiện theo timeline; cuối cùng các node hội tụ vào logo Reality Check AI và hiện câu kết bằng fade-in chậm 0,6 giây.
- Kết thúc ở trạng thái sạch, giữ logo và câu kết trên màn hình để chuyển sang Q&A.
- Nguồn: `adaptive-learning-system/docs/PROGRESS.md · TODO.md · README.md`.

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
