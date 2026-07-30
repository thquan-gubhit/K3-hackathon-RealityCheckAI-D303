# Reflection - Đàm Minh Tuấn (2A202601169)

## 1. Vai trò và Công việc đảm nhận
Trong dự án **Adaptive Learning System** (Hệ thống Học tập Thích ứng), tôi phụ trách các mảng cốt lõi: **Spec, Evaluator, Structure, Workflow & Prompts**. Cụ thể:
- Lên đặc tả yêu cầu (Spec) chi tiết, định nghĩa rõ ràng các kịch bản tương tác (Happy Path, Incomplete, Misconception, Hallucination, Low Confidence).
- Thiết kế luồng xử lý (Workflow) của AI Evaluator, đảm bảo hệ thống có thể bóc tách và đánh giá câu trả lời của học viên trên 4 phương diện (Đúng đắn, Bao phủ, Lập luận, Áp dụng).
- Tối ưu hóa System Prompt để ép LLM trả về cấu trúc JSON nhất quán.
- Xây dựng hệ thống Test tự động với Golden Set để đo lường chất lượng của AI Evaluator.

## 2. Những khó khăn gặp phải và Cách giải quyết
Khó khăn lớn nhất trong quá trình làm AI Product là đối mặt với **tính chất không đơn định (non-deterministic) của LLM**. 
- **Vấn đề:** Có những câu trả lời của học viên (ví dụ như trả lời cộc lốc hoặc thiếu ý), LLM đôi khi chấm điểm rất gắt, nhưng đôi khi lại châm chước. Điều này khiến cho hệ thống Test tự động (Golden Set) bị Fail ngẫu nhiên (Flaky tests).
- **Cách giải quyết:** Thay vì ép LLM phải ra một con số chính xác tuyệt đối, tôi đã thiết kế hệ thống chấm điểm dựa trên khoảng kỳ vọng (Expected Range). Đồng thời, tôi liên tục tinh chỉnh Prompt để vạch rõ ranh giới giữa `Correctness` (Đúng/Sai kiến thức) và `Coverage` (Đủ/Thiếu ý so với Rubric). Cuối cùng, tôi quyết định đặt Quality Bar ở mức 90% (thay vì 100%) để hệ thống đủ độ linh hoạt (robust) trước các dao động nhỏ của AI.

## 3. Bài học rút ra (Learnings)
- **Đo lường là then chốt:** Không thể làm AI Product nếu chỉ đánh giá bằng mắt (Eyeballing). Việc có một tập Golden Set 20 Test Cases và script chạy tự động đã giúp tôi mạnh dạn sửa Prompt nhiều lần mà không sợ hệ thống bị thoái hóa (Regression).
- **Luật cứng + AI mềm (Deterministic Rules + Non-deterministic AI):** Để tạo ra một ứng dụng giáo dục an toàn (tránh ảo giác), ta không thể giao phó 100% quyền quyết định cho AI. AI chỉ nên đóng vai trò phân tích ngôn ngữ (Language Parser), còn quyết định cuối cùng (như cho qua bài hay kích hoạt Tutor Agent) phải được quyết định bằng thuật toán if-else cứng dựa trên điểm số mà AI xuất ra.

## 4. Cảm nghĩ cá nhân
Hackathon này không chỉ rèn luyện kỹ năng viết Prompt, mà còn dạy tôi tư duy của một Product Manager / AI Engineer: *Làm sao để đưa một công nghệ khó đoán (LLM) vào một sản phẩm đòi hỏi độ tin cậy cực cao (Giáo dục).*
