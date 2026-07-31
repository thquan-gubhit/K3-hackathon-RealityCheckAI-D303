# Local Runbook

> **Delivery status:** MVP v1.0 was locally verified on Windows with Python
> 3.11.9. CI runs the same compile/dependency/test gates on Windows, Ubuntu,
> and macOS.

## System requirements

- Windows 10/11, Linux, or macOS.
- Python `3.11.x` (the project declares `>=3.11,<3.12`).
- `pip` and network access for the one-time dependency installation.
- A terminal with the project directory as the working directory.
- An OpenAI-compatible API key and model name for application startup. Tests use fake values and do not call a provider.

Confirm the runtime:

```bash
python --version
```

The result must report Python 3.11.

## Windows setup

Open PowerShell:

```powershell
cd adaptive-learning-system
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

If `py` is unavailable but `python --version` reports 3.11:

```powershell
python -m venv .venv
```

Edit `.env` and set at minimum:

```dotenv
LLM_API_KEY=your-provider-key
LLM_MODEL=your-model-name
```

Do not commit `.env`.

## Linux/macOS setup

```bash
cd adaptive-learning-system
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set non-empty `LLM_API_KEY` and `LLM_MODEL`. Set `LLM_BASE_URL` when using OpenRouter, another OpenAI-compatible endpoint, or a compatible local server.

## Initialize the database

With the virtual environment active:

```bash
python scripts/init_db.py
```

Expected message:

```text
Database initialized successfully.
```

The default database is `data/app.db`. Phases 1–5 create the document,
assessment, learning-state, misconception, and agent-trace tables and write
schema marker `PRAGMA user_version = 5`.

Optional offline demo seed:

```bash
python scripts/seed_demo.py
```

This idempotently creates a ready three-unit document and nine questions without
calling an LLM provider.

## Run the backend

Recommended:

```bash
python scripts/run_backend.py
```

Equivalent default development command:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Verify in another terminal:

```bash
curl --fail http://127.0.0.1:8000/health
```

Expected shape:

```json
{
  "status": "ok",
  "app_name": "Adaptive Learning System",
  "environment": "development",
  "database": "configured"
}
```

PowerShell alternative:

```powershell
Invoke-RestMethod -Method Get -Uri http://127.0.0.1:8000/health
```

Interactive API documentation is available at `http://127.0.0.1:8000/docs`.

## Run the frontend

Keep the backend running. In a second activated terminal:

```bash
python scripts/run_frontend.py
```

Equivalent default command:

```bash
streamlit run frontend/Home.py --server.address 127.0.0.1 --server.port 8501
```

Open `http://127.0.0.1:8501`. Use **Upload Document** to upload/process a
text-based PDF, **Knowledge Map** to inspect its units, **Study Session** to
answer adaptive questions, and **Progress Dashboard** to inspect mastery.

For the recommended zero-navigation flow, open **Auto Learning** and select a
PDF once. The page automatically uploads/processes it, creates the Knowledge
Map, starts the first KU session, and loads its first question. All source slides
assigned to the selected KU are displayed in the left column and the KU lesson
in the right column. Changing the KU automatically prepares its session.

Alternatively, keep only the backend running and open the integrated VLearn
reader at `http://127.0.0.1:8000/vlearn/`. Navigate to **Khóa học của tôi → Mở
khóa học**, choose a PDF, then use the KU list and Tutor panel. The backend
serves this UI on the same origin, so no second frontend process is required.

## Run tests

```bash
pytest -v
```

Optional coverage:

```bash
pytest --cov=app --cov=frontend --cov-report=term-missing
```

Default tests use fake settings and a fake structured LLM; they never contact a
real provider. The verified MVP v1.0 result is `122 passed` with one non-failing
upstream TestClient deprecation warning.

## Phase 1–5 demo

1. Initialize the database and start backend/frontend as above.
2. Open **Auto Learning** and select a text-based PDF.
3. Confirm the automatic pipeline reaches 100% coverage and shows the Knowledge
   Map without another button.
4. Confirm the source slides and selected KU appear side by side.
5. Change KU and confirm its lesson/question loads without re-uploading or
   re-processing the PDF.
6. Answer the generated Recall, Explain, and Apply questions.
7. Inspect separated correct/missing/incorrect feedback and mastery changes.
8. With `AGENT_ENABLED=true`, repeat a misconception and run the bounded tutor;
   with it `false`, confirm the normal next-question flow remains available.
9. Open **Progress Dashboard** to inspect dimensions and active misconceptions.

The original step-by-step Upload Document, Knowledge Map, and Study Session
pages remain available for inspection and manual retry workflows.

For the deterministic test fixture:

```bash
python scripts/create_demo_pdf.py
pytest -v tests/integration/test_document_processing_api.py
```

The integration test uses a fake LLM. Running the UI workflow uses the provider
configured in `.env`.

## Stop services

Press `Ctrl+C` in each backend/frontend terminal. Deactivate the environment when finished:

```bash
deactivate
```

## Troubleshooting

| Symptom | Likely cause | Recovery |
| --- | --- | --- |
| `python` or `py` is not recognized | Python 3.11 is not installed/on `PATH` | Install Python 3.11, reopen terminal, verify version |
| PowerShell blocks `Activate.ps1` | Execution policy prevents local scripts | Run `Set-ExecutionPolicy -Scope Process Bypass`, then activate again |
| Startup names `LLM_API_KEY`, `LLM_BASE_URL`, or `LLM_MODEL` | Required `.env` values are blank | Copy `.env.example` to `.env` and set provider values |
| `ModuleNotFoundError` | Venv inactive or dependencies missing | Activate `.venv`, then run `pip install -r requirements.txt` |
| Port 8000 or 8501 is in use | Another process owns the configured port | Stop it or change the corresponding `.env` port |
| Frontend reports backend unavailable | Backend is stopped or `BACKEND_API_URL` is wrong | Check `/health`, URL, host, port, and firewall |
| Database parent/path error | Invalid `DATABASE_URL` or permissions | Restore the default relative SQLite URL and rerun initialization |
| `database is locked` | Multiple writes/processes hold SQLite | Stop duplicate app processes and retry; do not delete the DB blindly |
| Provider timeout | Endpoint/model/network issue | Check provider settings; later LLM calls use bounded retries |
| PDF rejected as textless | Scanned/image-only PDF | Use a text-based PDF; OCR is outside this MVP |
| Processing returns `LLM_*` | Provider timeout/config/output problem | Check `.env`, provider availability, then retry within configured limits |
| Knowledge Map is not ready | Document was not processed or processing failed | Return to Upload Document and process/retry it |
| Agent returns `AGENT_DISABLED` | `AGENT_ENABLED=false` | Use deterministic remediation or explicitly enable it in `.env` |

## Operational safety

- Never paste an API key into a command that will be saved in shell history.
- Never log `.env` or authorization headers.
- Back up `data/app.db` before manual schema experiments.
- The MVP is a local development application, not a production deployment.
