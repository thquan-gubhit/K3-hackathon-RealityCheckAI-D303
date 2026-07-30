# Adaptive Learning System

## Thành viên nhóm và Phân công công việc

| STT | Họ và tên | Mã học viên | Vai trò / Phân công (Tham khảo Spec) |
|:---:|---|---|---|
| 1 | Trần Hoàng Quân | 2A202601805 | Structure, Workflow, Prompts & Evidence |
| 2 | Nguyễn Quang Hưng | 2A202601523 | UI |
| 3 | Lê Minh Khiêm | 2A202601645 | Canvas |
| 4 | Đàm Minh Tuấn | 2A202601169 | Spec, Evaluator, Structure, Workflow & Prompts |
| 5 | Đinh Huy Mạnh | 2A202601677 | Slide |
---

## Tóm tắt dự án

**Hệ thống Học tập Thích ứng (Adaptive Learning System)** là một ứng dụng AI thiết kế riêng cho những người tự học (self-directed learners). Hệ thống sinh ra để giải quyết triệt để tình trạng "đọc hiểu ngay nhưng gấp sách lại thì không thể giải thích được" (ảo giác hiểu biết), đồng thời khắc phục nhược điểm của phương pháp đọc đi đọc lại (rereading) vốn không giúp ghi nhớ dài hạn.

Thay vì thụ động chờ người dùng đặt câu hỏi như ChatGPT, hệ thống sẽ:
1. **Chủ động** đọc và chia nhỏ tài liệu PDF thành các Đơn vị Kiến thức (Knowledge Units).
2. **Ép người học tự kiểm chứng** (Retrieval Practice) bằng cách tự động sinh câu hỏi tự luận và Barem chấm điểm (Rubric) dựa sát vào nội dung bài.
3. **Đánh giá đa chiều:** AI (LLM) sẽ đóng vai trò Evaluator chấm điểm câu trả lời của học viên trên 4 phương diện (Đúng đắn, Bao phủ, Lập luận, Áp dụng). Hệ thống bóc tách rõ ràng ý nào học viên nói đúng, ý nào còn thiếu.
4. **Phát hiện hổng kiến thức (Remediation):** Nếu học viên liên tục mắc lỗi sai bản chất (Misconception), hệ thống sẽ đóng băng tiến độ và kích hoạt Tutor Agent (Gia sư AI) để can thiệp hướng dẫn tận tình.

Điểm nổi bật của dự án là tính an toàn và minh bạch. AI được "trói" bởi các Metric và tập luật tĩnh (Deterministic Rules) nghiêm ngặt để đảm bảo luôn bám sát tài liệu gốc (Source-grounded) và không bao giờ xảy ra tình trạng "ảo giác" (Hallucination) dẫn dắt sai người học.

