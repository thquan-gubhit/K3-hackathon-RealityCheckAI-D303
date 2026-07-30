# Adaptive Learning System

Nền tảng MVP học tập theo Active Recall thích ứng. Hệ thống được thiết kế với
workflow làm lõi, rule engine kiểm soát quyết định xác định, LLM xử lý tác vụ ngữ
nghĩa và Tutor Agent chỉ xử lý ngoại lệ.

Repository hiện hoàn thành **Phase 1 — Project foundation**: cấu hình từ `.env`,
SQLite/SQLAlchemy, FastAPI health check, Streamlit Home và test nền tảng. Xử lý
PDF, Knowledge Unit, câu hỏi, đánh giá, mastery và Tutor Agent thuộc các phase sau.

## Kiến trúc

Luồng phụ thuộc mục tiêu:

```text
Streamlit → FastAPI API → Workflow → Service → Rule/Agent → Repository → SQLite
```

Phase 1 hiện thực phần giao diện nền, API, cấu hình và kết nối database. Các lớp
nghiệp vụ đã được dành chỗ trong cấu trúc project nhưng chưa được triển khai sớm
hơn kế hoạch.

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
| File storage | `UPLOAD_DIR`, `MAX_UPLOAD_SIZE_MB` | Chuẩn bị cho Phase 2 |
| LLM | `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL` | Provider tương thích OpenAI |
| Rules/Mastery/Agent | `KU_*`, `QUESTION_*`, `MASTERY_*`, `AGENT_*` | Ngưỡng deterministic cho các phase sau |

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

Mở <http://127.0.0.1:8501>. Home page sẽ gọi `GET /health`, hiển thị trạng thái
kết nối và hướng dẫn khắc phục khi backend chưa sẵn sàng.

## Chạy test

```bash
pytest -v
```

Kèm coverage:

```bash
pytest --cov=app --cov=frontend --cov-report=term-missing
```

Suite Phase 1 hiện có 15 test, đã pass trên Python 3.11.9 với coverage tổng
89% cho `app` và `frontend`. Test không gọi API LLM thật và sử dụng database
tạm khi cần.

## Demo flow Phase 1

1. Sao chép `.env.example` thành `.env` và điền cấu hình bắt buộc.
2. Chạy `python scripts/init_db.py`.
3. Khởi động backend; gọi `GET /health` và xác nhận trạng thái `ok`.
4. Khởi động Streamlit; xác nhận Home page kết nối được backend.
5. Chạy `pytest -v`.

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

Phase 1 chưa upload/parse PDF, chưa tạo Knowledge Map, chưa sinh hoặc chấm câu
hỏi, chưa cập nhật mastery và chưa chạy Tutor Agent. Trạng thái chính xác của
từng hạng mục được theo dõi trong [PROGRESS.md](docs/PROGRESS.md) và
[TODO.md](docs/TODO.md).
