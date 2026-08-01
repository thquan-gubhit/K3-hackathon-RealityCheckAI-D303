# Kịch bản Pitching: Hệ thống Học tập Thích ứng (Adaptive Learning System)

Kịch bản này được xây dựng bám sát 6 yêu cầu, dựa trên tài liệu đặc tả `spec.md`, các tài liệu trong `docs/` và thư mục `reflection/`.

---

## 1. Painpoint rõ ràng + Actor (Dựa trên khảo sát thực tế)
**Đối tượng (Actor):** Những người tự học (Self-directed learners) và sinh viên/học viên các khóa học chuyên sâu.
**Nỗi đau (Painpoint):** 
Học viên thường xuyên mắc phải **"Ảo giác hiểu biết" (Illusion of competence)**. Khi đọc một tài liệu PDF hoặc slide bài giảng, họ gật gù tưởng mình đã hiểu, nhưng không thể tự giải thích lại hay áp dụng.
- **Dữ liệu khảo sát thực tế (Evidence):** Nhóm đã thực hiện khảo sát trên 17 người học (n=17). Kết quả cho thấy **đa số sinh viên thừa nhận chiến lược học tập chính của họ chỉ là "đọc đi đọc lại slide" (rereading) trước kỳ thi, và họ chỉ nhận ra mình hổng kiến thức khi bước vào phòng thi hoặc làm bài kiểm tra** 
- Người học cho biết họ gặp tình trạng "đọc hiểu ngay nhưng lúc thi hoặc làm bài tập thì không biết giải thích từ đâu: 
    - 23.5% rất thường xuyên.
    - 47.1% thường xuyên.
    - 29,4% thỉnh thoảng.

## 2. Giải pháp: Workflow + Scope (MVP / Could / Should / Won't have)
**Giải pháp:** Một hệ thống biến việc đọc thụ động thành thực hành gợi nhớ chủ động (Active Recall).

**Workflow (Luồng hoạt động):**
1. **Xử lý tài liệu:** Upload PDF ➔ AI bóc tách thành các Đơn vị Kiến thức (Knowledge Units) ngắn (2-10 phút đọc).
2. **Sinh câu hỏi & Barem:** Sinh ra câu hỏi (Recall, Explain, Apply) kèm theo Barem chấm điểm (Rubric) ẩn được tạo *trước* khi người học trả lời.
3. **Đánh giá & Phản hồi:** Học viên trả lời ➔ Hệ thống chấm điểm đa chiều (Correctness, Coverage, Reasoning, Application).
4. **Thích ứng & Can thiệp:** Cập nhật độ thông thạo (Mastery). Nếu phát hiện lỗi sai bản chất (Misconception), hệ thống gọi Gia sư (Tutor Agent) vào can thiệp 1-1.

**Phạm vi sản phẩm:**
- **Must have (MVP):** Pipeline xử lý PDF thành Knowledge Units; Sinh câu hỏi bám sát tài liệu (Source-grounded); Đánh giá câu trả lời theo 4 chiều cốt lõi; Tính toán điểm Mastery bằng thuật toán tĩnh.
- **Should have / Could have:** Đo lường chiều đánh giá thứ 5: **Delayed Retention (Ôn tập ngắt quãng)** để kiểm tra trí nhớ dài hạn. Tutor Agent can thiệp giải thích lỗi sai (Remediation) khi học viên mắc Misconception nghiêm trọng.
- **Won't have:** Chatbot AI tự do (unbounded chat). LLM không được quyền tự quyết định cho học viên qua bài.

## 3. Điểm sáng của giải pháp & Rule đánh giá độ hiểu bài
**Điểm sáng cốt lõi:** Hệ thống sử dụng **Rule Engine tĩnh bọc bên ngoài LLM** để kiểm soát hoàn toàn AI. LLM chỉ đóng vai trò phân tích ngữ nghĩa, còn quyền quyết định (Policy) thuộc về code.

**Rule đánh giá độ hiểu bài & Cơ sở khoa học chứng minh:**
Hệ thống không đánh giá cảm tính mà ép LLM chấm điểm dựa trên 5 chiều đánh giá (4 chiều MVP + 1 chiều mở rộng). Các tiêu chí này được xây dựng trên nền tảng khoa học giáo dục vững chắc:

| Tiêu chí đánh giá của dự án | Cơ sở nghiên cứu (Paper) | Vì sao chọn tiêu chí này |
|---|---|---|
| **Correctness** *(Đúng đắn / Retrieval Accuracy)* | Roediger & Karpicke (2006), *Test-Enhanced Learning* | Paper kinh điển chứng minh việc chủ động nhớ lại (Active Recall) mang lại hiệu quả tốt hơn hẳn so với rereading (chỉ đọc lại). |
| **Coverage** *(Bao phủ / Completeness)* | Mislevy & Haertel (2006), *Implications of Evidence-Centered Design for Educational Testing* | Đặt nền tảng cho việc đánh giá học viên dựa trên các bằng chứng cụ thể (evidence) có trong Barem, không chỉ nhìn vào điểm số chung chung. |
| **Reasoning** *(Lập luận / Relational Understanding)* | Chi & Wylie (2014), *The ICAP Framework* | Chứng minh việc học viên tự giải thích và tạo mối quan hệ giữa các khái niệm tạo ra mức độ học sâu hơn là nhớ lại đơn thuần. |
| **Application** *(Ứng dụng / Transfer)* | Bransford & Schwartz (1999), *Rethinking Transfer* | Chứng minh khả năng áp dụng kiến thức vào trong các ngữ cảnh mới là bằng chứng xác đáng nhất của sự hiểu sâu. |
| **Delayed Retention** *(Ôn tập ngắt quãng / Spacing Effect - Mở rộng)* | Dunlosky et al. (2013), *Strengthening the Student Toolbox* | Nghiên cứu Meta-review xác định Practice Testing và Distributed Practice (học ngắt quãng) là hai chiến lược có hiệu quả cao nhất cho ghi nhớ dài hạn. |

## 4. Metric chứng minh hệ thống hoạt động đúng và chính xác
Hệ thống không dựa vào cảm giác mà được nghiệm thu qua các metric định lượng rõ ràng:
1. **Bộ dữ liệu vàng (Golden Set 20 Test Cases):** Hệ thống được test qua 20 kịch bản giả định (từ *Happy Path* trả lời chuẩn, đến *Incomplete* trả lời thiếu ý, và *Misconception* hiểu sai bản chất). Đảm bảo LLM chấm đúng điểm kỳ vọng và bắt trúng 100% lỗi sai bản chất.
2. **Metric `Confidence` (Van an toàn):** Nếu người dùng trả lời lấp lửng, độ tự tin của Evaluator `< 0.5`, hệ thống từ chối chấm điểm và yêu cầu giải thích thêm (Graceful Failure) chứ không đánh rớt oan.
3. **Luật MASTERED (Thông thạo) khắt khe:** Không một câu trả lời đơn lẻ nào có thể giúp học viên qua bài. Học viên chỉ đạt `MASTERED` khi:
   - Điểm tích lũy `mastery_score >= MASTERY_THRESHOLD`
   - Đã trả lời đủ số lượng câu hỏi độc lập (`MIN_QUESTIONS_FOR_MASTERY`)
   - Có bằng chứng về khả năng áp dụng (`has_application_evidence = true`)
   - **Không có bất kỳ Misconception nào chưa được giải quyết.**

## 5. So sánh với các sản phẩm khác
- **NotebookLM (Google):** Quá thụ động. Chỉ tổng hợp và trả lời khi user hỏi, không chủ động tạo ra luồng kiểm tra (Testing) và không theo dõi được độ thông thạo (Mastery) của người học.
- **Khanmigo (Khan Academy):** Thường sử dụng phương pháp Socratic (hỏi vặn ngược lại) quá đà trên mọi tình huống, khiến người học mệt mỏi và tốn thời gian.
- **Adaptive Learning System của chúng tôi:** Đóng vai trò như một **Giám khảo công tâm**, đưa ra câu hỏi, có barem rõ ràng. Hệ thống chỉ dùng Socratic/Tutor Agent để can thiệp 1-1 khi bạn **thực sự hiểu sai bản chất**. Khi bạn trả lời thiếu, nó chỉ đơn giản chỉ ra ý thiếu và yêu cầu bổ sung.

## 6. Summary (Tổng kết)
Hệ thống Học tập Thích ứng của chúng tôi đi từ **painpoint thực tế đã được khảo sát chứng minh**, sử dụng **cơ sở khoa học về Retrieval Practice**, và được hiện thực hóa bằng một **kiến trúc phần mềm an toàn (Deterministic Rule Engine + Bounded Agent)**. 

Thay vì tạo ra một con chatbot nói chuyện phiếm, chúng tôi tạo ra một "Cỗ máy sư phạm" minh bạch, có Barem rõ ràng, có điểm số định lượng, và quan trọng nhất: **Ép người học phải thực sự hiểu bài thì mới được phép đi tiếp**. Đây chính là cách AI định hình lại giáo dục một cách an toàn và thực chất nhất.
