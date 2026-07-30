# Source of Truth — Reality Check AI

Tài liệu này ghi thứ tự ưu tiên nguồn khi chuẩn bị spec, slide và demo trên nhánh `Manh`.

## 1. User & Job

Nguồn chính thức: `spec.md` §1.

- **Job executor:** học viên tự học.
- **Bối cảnh:** vừa đọc một tài liệu PDF dài/phức tạp.
- **Workflow:** đọc → tóm tắt → gấp tài liệu → nhớ lại/giải thích → kiểm tra hiểu đúng hay sai.
- **Core JTBD:** tự kiểm chứng mức độ hiểu và khả năng giải thích văn bản dài ngay sau khi đọc để tránh ảo giác hiểu biết.
- **Current alternatives:** đọc lại tài liệu hoặc đưa nội dung vào ChatGPT để tạo câu hỏi.
- **Pain:** rereading không tạo đủ bằng chứng retrieval; feedback từ chatbot có thể hallucinate, generic hoặc không bám rubric riêng.
- **Evidence khảo sát được ghi trong spec:** `n=17`; 23,5% rất thường xuyên, 47,1% thường xuyên và 29,4% thỉnh thoảng gặp tình trạng đọc hiểu nhưng không biết giải thích khi thi/làm bài.
- **Số tổng hợp dùng trên slide:** 70,6% thường xuyên hoặc rất thường xuyên.

Các nghiên cứu về rereading, retrieval practice, hallucination và feedback generic được liệt kê kèm liên kết trong `spec.md` §1.

## 2. Hướng và lát cắt

Nguồn chính thức: phần đầu `spec.md` và §4.

- **Tên trình bày:** Reality Check AI.
- **Hướng:** C — Làn mở.
- **Loại:** tính năng mới.
- **Prototype:** Working.
- **Lát cắt:** học viên trả lời câu hỏi tự luận; evaluator chấm theo tài liệu/rubric; hệ thống trả feedback đúng–thiếu–sai và cập nhật mastery.
- **Automation:** Conditional.

## 3. Sản phẩm đã build

Nguồn chính thức: `adaptive-learning-system/` và tài liệu trong `adaptive-learning-system/docs/`.

```text
PDF → Knowledge Units → Recall/Explain/Apply
→ reference answer + rubric bất biến
→ evaluation correct/missing/incorrect/misconception
→ deterministic next action + mastery
→ bounded Tutor Agent cho ngoại lệ
```

- Streamlit + FastAPI + SQLite.
- Workflow là backbone; rule giữ quyền policy; LLM xử lý tác vụ ngữ nghĩa.
- Tutor Agent optional, giới hạn bước, allow-list tool và có trace.
- Không đạt `MASTERED` chỉ từ một câu trả lời.
- Confidence thấp dẫn đến `ASK_CLARIFICATION`.

## 4. Kết quả và kiểm thử

Nguồn chính thức: `spec.md` §7, `adaptive-learning-system/eval/golden_set.json` và `adaptive-learning-system/docs/PROGRESS.md`.

- Golden set: 20 case.
- Cơ cấu: 4 Happy Path, 4 Incomplete, 5 Misconception, 4 Hallucination, 3 Low Confidence.
- Quality bar: ≥90%.
- Kết quả được báo cáo trong spec: 75% → 100%.
- Engineering suite: 100 tests passed.
- Fixture: 3 trang → 3 Knowledge Units hợp lệ → coverage 100%.
- Giới hạn: repo chưa lưu output log độc lập cho hai lượt eval; default engineering tests dùng fake structured model.

## 5. Validation

Repo chưa có thư mục/log validation và chưa có quote user test có tên. Không tạo quote giả cho slide 5; giữ placeholder cho tới khi có log thật.

## 6. Nhóm và phân công

Nguồn chính thức: `TEAMMATE.md` và `adaptive-learning-system/README.md`.

| Thành viên | Mã học viên | Vai trò |
|---|---|---|
| Trần Hoàng Quân | 2A202601805 | Bằng chứng |
| Đinh Huy Mạnh | 2A202601677 | Prompt |
| Nguyễn Quang Hưng | 2A202601523 | Build |
| Lê Minh Khiêm | 2A202601645 | Spec |
| Đàm Minh Tuấn | 2A202601169 | Validation |

