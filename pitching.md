# Kịch bản Pitching 5 phút: Hệ thống Học tập Thích ứng (Adaptive Learning System)

**Thời lượng:** 5 phút (~600-700 chữ)
**Người trình bày:** Đại diện nhóm
**Mục tiêu:** Thuyết phục ban giám khảo về tính cấp thiết của vấn đề "ảo giác hiểu biết" và giải pháp cá nhân hóa, an toàn của hệ thống.

---

## 1. Mở đầu & Đặt vấn đề (0:00 - 1:00)

**(Slide 1: Tiêu đề dự án & Hook - Câu hỏi tương tác)**

**[MC]:** 
"Xin chào ban giám khảo và toàn thể hội trường. Bao nhiêu người trong số chúng ta ở đây từng gặp tình trạng: Đọc xong một tài liệu dài, gật gù tưởng mình đã hiểu, nhưng đến khi gấp sách lại hoặc vào phòng thi thì... đầu óc trống rỗng, không thể giải thích được bằng lời của mình? 

Đó chính là hiện tượng **'Ảo giác hiểu biết'** – một vấn đề nhức nhối với những người tự học (self-directed learners). 

**(Slide 2: Nỗi đau của người tự học)**

Hiện nay, chúng ta thường giải quyết bằng hai cách: 
Thứ nhất là **đọc đi đọc lại (Rereading)**. Nhưng nghiên cứu khoa học chỉ ra: đọc lại tạo ra cảm giác quen thuộc giả tạo, hoàn toàn không giúp ghi nhớ dài hạn. 
Thứ hai là **nhờ ChatGPT tạo câu hỏi**. Nhưng ChatGPT lại gặp vấn đề về 'ảo giác' (hallucination), hay nói lan man ngoài lề, và đánh giá rất chung chung, khiến chúng ta không biết mình thực sự đang hổng kiến thức ở đâu.

Để giải quyết triệt để nỗi đau này, nhóm chúng tôi mang đến: **Hệ thống Học tập Thích ứng (Adaptive Learning System)**."

---

## 2. Giải pháp cốt lõi (1:00 - 2:15)

**(Slide 3: Tổng quan giải pháp - Workflow 4 bước)**

**[MC]:** 
"Sản phẩm của chúng tôi biến trải nghiệm đọc thụ động thành **Retrieval Practice** (chủ động gợi nhớ). Thay vì đợi bạn hỏi như ChatGPT, hệ thống của chúng tôi sẽ chủ động dẫn dắt bạn qua 4 bước:

1. **Bóc tách thông minh:** Đưa cho hệ thống 1 file PDF, AI sẽ tự động phân tích và chia nhỏ thành các 'Đơn vị kiến thức' (Knowledge Units) vừa sức học.
2. **Ép tự kiểm chứng:** AI chủ động sinh ra câu hỏi tự luận bám sát ngữ cảnh, kèm theo Barem chấm điểm (Rubric) ẩn.
3. **Chấm điểm Đa chiều:** Khi bạn trả lời, AI (đóng vai trò Evaluator) sẽ chấm điểm dựa trên 4 tiêu chí: Tính đúng đắn, Độ bao phủ ý, Tư duy lập luận, và Khả năng áp dụng. Nó bóc tách rõ ràng: Bạn nói đúng ý nào, thiếu ý nào.
4. **Gia sư can thiệp (Remediation):** Nếu bạn hiểu sai bản chất (Misconception), hệ thống lập tức đóng băng tiến độ, kích hoạt 'Gia sư AI' vào hướng dẫn 1-1 cho đến khi bạn thực sự vượt qua."

---

## 3. Demo & Trải nghiệm thực tế (2:15 - 3:30)

**(Slide 4: Video Demo/Screenshot giao diện Happy Path & Fail Path)**

**[MC]:** 
"Mời ban giám khảo nhìn lên màn hình. 
Khi một học viên học về khái niệm 'Machine Learning'. 
- **Happy Path:** Nếu trả lời đủ ý, hệ thống khen ngợi, cộng điểm Mastery và mở khóa bài tiếp theo.
- **Fail Path / Low Confidence:** Nếu học viên trả lời cộc lốc: 'Nó giảm'. AI của chúng tôi đủ thông minh để nhận ra độ tự tin thấp, nó không đánh rớt ngay mà hỏi vặn lại: *'Bạn có thể giải thích rõ hơn Nó là gì không?'* (Nguyên tắc Thu hẹp phạm vi).
- **Đặc biệt (Misconception):** Nếu học viên nói: *'Data leakage là hiện tượng hỏng ổ cứng'* – Một lỗi sai bản chất nghiêm trọng! Hệ thống ngay lập tức bắt lỗi, trừ điểm nặng và buộc học viên làm việc với AI Tutor thay vì cho qua bài."

---

## 4. Lợi thế cạnh tranh & Tính minh bạch (3:30 - 4:15)

**(Slide 5: So sánh với NotebookLM và Khanmigo)**

**[MC]:** 
"Bạn có thể hỏi: Chúng tôi khác gì Google NotebookLM hay Khanmigo?
- Với **NotebookLM**, nó quá thụ động, chỉ trả lời khi bạn hỏi và không theo dõi được tiến độ (Mastery).
- Với **Khanmigo**, nó thường hỏi vặn lại Socratic liên tục khiến người học nản lòng.
- **Còn chúng tôi:** Kết hợp cả hai. Chúng tôi dùng hệ thống **luật tĩnh (Deterministic Rules)** bọc bên ngoài LLM để đảm bảo an toàn tuyệt đối 100%. Barem (Rubric) luôn được tạo ra *trước* khi bạn trả lời, đảm bảo tính **minh bạch (Explainability)**. LLM bị cấm tuyệt đối việc vay mượn kiến thức ngoài PDF, loại bỏ hoàn toàn rủi ro Hallucination."

---

## 5. Tổng kết & Tương lai (4:15 - 5:00)

**(Slide 6: Team & Tương lai)**

**[MC]:**
"Hệ thống của chúng tôi đã được kiểm thử qua bộ 20 Test Cases (Golden Set) khắt khe, đạt tỷ lệ đánh giá đúng 100% trong việc nhận diện lỗi thiếu ý và lỗi hiểu sai bản chất. 

Chúng tôi là nhóm [X], với đội ngũ bao gồm: Spec & Evaluator, Prompt Engineering, UI và Canvas. 

Tầm nhìn của chúng tôi không chỉ dừng lại ở hackathon này, mà là tạo ra một công cụ học tập không thể thiếu cho bất kỳ sinh viên hay chuyên gia nào muốn làm chủ tri thức mới một cách sâu sắc và bền vững nhất. Đừng đọc lại, hãy để hệ thống của chúng tôi 'ép' bạn giỏi lên.

Xin cảm ơn ban giám khảo đã lắng nghe!"

---

## Phụ lục / Tech Deep Dive: AI của chúng tôi đánh giá người dùng như thế nào? 
*(Sử dụng cho vòng Q&A hoặc nếu ban giám khảo hỏi sâu về công nghệ)*

**[MC / Technical Lead]:**
"Nếu ban giám khảo thắc mắc làm sao chúng tôi tránh được việc AI 'chấm điểm cảm tính', thì đây là bí quyết. Hệ thống của chúng tôi không dùng một prompt chung chung, mà ép AI hoạt động như một cỗ máy chấm thi dựa trên dữ liệu cấu trúc (Structured Data) với 3 lớp bảo vệ:

**Thứ nhất: Chấm điểm 4 chiều (4-Dimension Scores)**
AI bắt buộc phải đánh giá câu trả lời trên thang điểm từ 0 đến 1 ở 4 thước đo độc lập:
1. **Tính đúng đắn (Correctness):** Có nói sai sự thật không?
2. **Độ bao phủ (Coverage):** Có đủ các ý mà Barem yêu cầu không? (Nói đúng nhưng thiếu ý thì chỉ bị trừ Coverage chứ không trừ Correctness).
3. **Lập luận (Reasoning):** Có hiểu được nguyên nhân - kết quả không?
4. **Tính ứng dụng (Application):** Có biết áp dụng vào thực tế không?

**Thứ hai: Bóc tách Feedback rõ ràng**
AI không được phép trả về một đoạn văn nhận xét. Nó phải bóc tách dữ liệu thành các mảng rõ ràng: `Ý đúng`, `Ý thiếu`, `Ý sai`.
Đặc biệt là mảng **`Misconceptions` (Hiểu sai bản chất)**: Chỉ cần AI bắt được 1 lỗi hiểu sai cốt lõi, tiến độ bài học lập tức bị đóng băng để xử lý triệt để, không cho phép học viên 'lướt' qua.

**Thứ ba: Van an toàn bằng Độ tự tin (Confidence Metric)**
Khi học viên trả lời cộc lốc hoặc dùng mẹo đoán mò, AI không đủ dữ kiện để đánh giá. Lúc này, metric `Confidence` sẽ tụt xuống dưới `0.50`. Thay vì đánh rớt oan uổng, hệ thống từ chối chấm điểm và kích hoạt cờ `ASK_CLARIFICATION`, yêu cầu học viên: *'Hãy giải thích rõ hơn ý của bạn'*. Đây là thiết kế theo chuẩn Graceful Failure (Thất bại êm đẹp) của Google PAIR.

Và cuối cùng, tất cả các điểm số này sẽ chạy qua một Rule Engine tĩnh để tính toán ra điểm **Mastery (Độ thông thạo)**. Trạng thái chỉ chuyển sang 'Hoàn thành' khi bạn có đủ bằng chứng hiểu bài và tuyệt đối không còn Misconception nào!"
