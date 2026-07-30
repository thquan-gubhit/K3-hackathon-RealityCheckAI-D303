# Adaptive Learning System

Nền tảng MVP học tập theo Active Recall thích ứng. Hệ thống được thiết kế với
workflow làm lõi, rule engine kiểm soát quyết định xác định, LLM xử lý tác vụ ngữ
nghĩa và Tutor Agent chỉ xử lý ngoại lệ.

Repository hiện hoàn thành và kiểm thử **Phase 1–5**: xử lý PDF/Knowledge Map,
sinh câu hỏi Recall–Explain–Apply có rubric bất biến, đánh giá câu trả lời, điều
phối phiên học và mastery bằng rule xác định, cùng Tutor Agent giới hạn bước,
allow-list tool và có audit trace.

## Nhóm & phân công

| Thành viên | Mã học viên | Vai trò chính | Trách nhiệm và đầu ra |
|---|---|---|---|
| Trần Hoàng Quân | 2A202601805 | Bằng chứng | Mining chatlog, xác định phương pháp đếm, lưu các ví dụ có mã nguồn, tổng hợp số liệu pain/impact và kiểm tra các kết luận trong spec có thể truy ngược về evidence. |
| Đinh Huy Mạnh | 2A202601677 | Prompt | Thiết kế và thử nghiệm prompt cho Knowledge Unit, câu hỏi Recall–Explain–Apply, rubric, đánh giá câu trả lời và Tutor Agent; ghi nhận phiên bản prompt, lỗi và thay đổi sau mỗi lượt thử. |
| Nguyễn Quang Hưng | 2A202601523 | Build | Phát triển và tích hợp prototype FastAPI–Streamlit, workflow học thích ứng, rule engine, persistence và luồng demo; bảo đảm phần chạy thật có thể khởi động và trình diễn ổn định. |
| Lê Minh Khiêm | 2A202601645 | Spec | Duy trì `spec.md`, liên kết quyết định sản phẩm với evidence, chốt lát cắt/non-goals/automation/quality bar và cập nhật changelog khi thiết kế thay đổi. |
| Đàm Minh Tuấn | 2A202601169 | Validation | Lập kế hoạch user test, chuẩn bị task và câu hỏi, ghi feedback/quote có tên hoặc vai, tổng hợp vấn đề lặp lại và đề xuất thay đổi trước demo. |

### Cách phối hợp

- **Quân → Khiêm:** bàn giao evidence log, số liệu và giới hạn của dữ liệu để đưa vào §1–§2 mà không suy diễn quá mức.
- **Khiêm → Mạnh & Hưng:** chốt lát cắt, hành vi mong muốn và các case khó để prompt và prototype cùng thực hiện một spec.
- **Mạnh ↔ Hưng:** tích hợp prompt vào workflow, lưu output/trace cần thiết và kiểm tra fallback khi output không hợp lệ hoặc thiếu căn cứ.
- **Tuấn → cả nhóm:** đưa feedback validation về changelog; nhóm ưu tiên sửa lỗi ảnh hưởng trực tiếp đến core JTBD và đường demo.
- Mỗi thành viên chịu trách nhiệm giải thích được phần có tên mình trong buổi xác minh và demo.

## Kiến trúc

Luồng phụ thuộc mục tiêu:

```text
Streamlit → FastAPI API → Workflow → Service → Rule/Agent → Repository → SQLite
```

Luồng `API → Workflow → Service → Rule/Agent → Repository` được hiện thực cho
toàn bộ MVP. Endpoint không gọi LLM trực tiếp; output LLM luôn qua Pydantic.
Workflow/rule điều khiển đường đi chính, agent chỉ chạy khi cấu hình và trigger
cho phép.

## Requirements

- Python 3.11
- `pip`
- Windows, Linux hoặc macOS
- API key và model của một dịch vụ tương thích OpenAI

## Quick start

Chạy các lệnh từ thư mục `adaptive-learning-system`.

### 1. Tạo virtual environment

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```bat
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

### 2. Cài dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Tạo `.env`

Windows:

```bat
copy .env.example .env
```

Linux/macOS:

```bash
cp .env.example .env
```

Mở `.env` và điền tối thiểu:

```dotenv
LLM_API_KEY=your-api-key
LLM_MODEL=your-model-name
```

`LLM_BASE_URL` đã có endpoint mẫu trong `.env.example`; giữ giá trị đó hoặc đổi
sang endpoint tương thích của provider. Không commit `.env`. Ứng dụng từ chối
khởi động với thông báo hướng dẫn nếu thiếu key, base URL hoặc model, và API key
không được đưa vào log.

## Cấu hình `.env`

Các nhóm cấu hình chính:

| Nhóm | Biến tiêu biểu | Mục đích |
|---|---|---|
| Application | `APP_NAME`, `APP_ENV`, `DEBUG`, `LOG_LEVEL` | Metadata và logging |
| Backend | `BACKEND_HOST`, `BACKEND_PORT` | FastAPI/Uvicorn |
| Frontend | `FRONTEND_HOST`, `FRONTEND_PORT`, `BACKEND_API_URL` | Streamlit và địa chỉ API |
| Database | `DATABASE_URL` | SQLAlchemy connection URL |
| File storage | `UPLOAD_DIR`, `MAX_UPLOAD_SIZE_MB` | Lưu PDF Phase 2 an toàn |
| LLM | `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL` | Provider tương thích OpenAI |
| Rules/Mastery/Agent | `KU_*`, `QUESTION_*`, `MASTERY_*`, `AGENT_*` | Ngưỡng deterministic và giới hạn agent |

Danh sách đầy đủ và giá trị mặc định nằm trong [`.env.example`](.env.example).

## Khởi tạo database

```bash
python scripts/init_db.py
```

Lệnh tạo thư mục dữ liệu nếu cần, tạo các bảng SQLAlchemy đã đăng ký và kiểm tra
kết nối SQLite. File local `data/app.db` được loại khỏi Git.

## Chạy backend

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Hoặc:

```bash
python scripts/run_backend.py
```

Kiểm tra:

```bash
curl http://127.0.0.1:8000/health
```

Tài liệu OpenAPI: <http://127.0.0.1:8000/docs>.

## Chạy frontend

Mở terminal thứ hai, kích hoạt cùng virtual environment, rồi chạy:

```bash
streamlit run frontend/Home.py --server.address 127.0.0.1 --server.port 8501
```

Hoặc:

```bash
python scripts/run_frontend.py
```

Mở <http://127.0.0.1:8501>. Home kiểm tra backend; các trang hỗ trợ upload/xử lý
PDF, xem Knowledge Map, học theo câu hỏi thích nghi và theo dõi tiến độ.

## Chạy test

```bash
pytest -v
```

Kèm coverage:

```bash
pytest --cov=app --cov=frontend --cov-report=term-missing
```

Suite qua Phase 5 hiện có 99 test. Test dùng fake structured LLM, không gọi API
thật, và dùng database SQLite tạm khi cần.

## Demo flow Phase 1–5

1. Sao chép `.env.example` thành `.env` và điền cấu hình bắt buộc.
2. Chạy `python scripts/init_db.py`.
3. Khởi động backend; gọi `GET /health` và xác nhận trạng thái `ok`.
4. Khởi động Streamlit, upload một PDF có text và chọn **Process document**.
5. Xác nhận trạng thái `ready`, coverage 100% và mở **Knowledge Map**.
6. Mở **Study Session**, chọn tài liệu/KU, đọc unit, trả lời lần lượt các câu hỏi
   và quan sát feedback/mastery.
7. Lặp lại một misconception để kiểm tra Tutor Agent khi `AGENT_ENABLED=true`;
   đặt `false` để xác nhận workflow học thông thường vẫn hoạt động.
8. Mở **Progress Dashboard** và chạy `pytest -v`.

## Cấu trúc chính

```text
app/          FastAPI, cấu hình và database
frontend/     Streamlit UI
tests/        Unit/integration tests
data/         SQLite local và vùng upload
docs/         Thiết kế, quyết định, tiến độ và runbook
scripts/      Lệnh tiện ích khởi tạo/chạy ứng dụng
```

## Tài liệu

- [00 — Overview](docs/00_OVERVIEW.md)
- [01 — Business requirements](docs/01_BUSINESS_REQUIREMENTS.md)
- [02 — System architecture](docs/02_SYSTEM_ARCHITECTURE.md)
- [03 — Knowledge Unit design](docs/03_KNOWLEDGE_UNIT_DESIGN.md)
- [04 — Question design](docs/04_QUESTION_DESIGN.md)
- [05 — Evaluation and mastery](docs/05_EVALUATION_AND_MASTERY.md)
- [06 — Workflows](docs/06_WORKFLOWS.md)
- [07 — Rule engine](docs/07_RULE_ENGINE.md)
- [08 — Tutor Agent](docs/08_TUTOR_AGENT.md)
- [09 — Data model](docs/09_DATA_MODEL.md)
- [10 — API specification](docs/10_API_SPECIFICATION.md)
- [11 — Test plan](docs/11_TEST_PLAN.md)
- [12 — Runbook](docs/12_RUNBOOK.md)
- [Architecture decisions](docs/DECISIONS.md)
- [Progress](docs/PROGRESS.md)
- [TODO](docs/TODO.md)
- [Vibe coding log](docs/VIBE_CODING_LOG.md)

## Giới hạn hiện tại

Xử lý hiện đồng bộ; PDF scan không có text cần OCR nên nằm ngoài MVP. Lịch sử
local chưa có migration/export và chưa có xác thực đa người dùng. Trạng thái
chính xác được theo dõi trong [PROGRESS.md](docs/PROGRESS.md) và
[TODO.md](docs/TODO.md).
