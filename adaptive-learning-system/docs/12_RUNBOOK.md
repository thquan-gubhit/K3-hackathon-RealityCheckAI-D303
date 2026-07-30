# Local Runbook

> **Delivery status:** The Phase 1 run instructions were verified on Windows
> with Python 3.11.9: database initialization, backend health, Streamlit startup,
> Home-page execution, and the 15-test suite all succeeded. PDF and learning-flow
> commands become meaningful only after their later phases are implemented.

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

The default database is `data/app.db`. Phase 1 creates the configured SQLite file and any currently registered tables; later phases register domain tables.

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

Open `http://127.0.0.1:8501`. The Phase 1 home page checks `BACKEND_API_URL` and does not implement PDF processing or study sessions.

## Run tests

```bash
pytest -v
```

Optional coverage:

```bash
pytest --cov=app --cov=frontend --cov-report=term-missing
```

Default tests use fake settings and do not require a real LLM request.

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
| PDF controls are absent | Expected in Phase 1 | Continue with Phase 2 implementation; Phase 1 includes only the home page |
| Agent endpoint is absent | Expected in Phase 1 | Tutor Agent is scheduled for Phase 5 |

## Operational safety

- Never paste an API key into a command that will be saved in shell history.
- Never log `.env` or authorization headers.
- Back up `data/app.db` before manual schema experiments.
- The MVP is a local development application, not a production deployment.
