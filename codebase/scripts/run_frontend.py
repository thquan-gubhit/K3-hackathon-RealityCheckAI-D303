"""Run the Streamlit frontend with values loaded from application settings."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from dotenv import dotenv_values


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    """Start Streamlit and return its exit code."""
    env = os.environ.copy()
    env.setdefault("PYTHONPATH", str(PROJECT_ROOT))
    dotenv_content = dotenv_values(PROJECT_ROOT / ".env")
    file_settings = {
        name: dotenv_content.get(name)
        for name in ("FRONTEND_HOST", "FRONTEND_PORT", "BACKEND_API_URL")
    }
    del dotenv_content
    for name in ("FRONTEND_HOST", "FRONTEND_PORT", "BACKEND_API_URL"):
        value = file_settings.get(name)
        if name not in env and value:
            env[name] = value

    # The Streamlit process never calls the LLM provider.
    env.pop("LLM_API_KEY", None)
    host = env.get("FRONTEND_HOST", "127.0.0.1")
    port = env.get("FRONTEND_PORT", "8501")

    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(PROJECT_ROOT / "frontend" / "Home.py"),
        "--server.address",
        host,
        "--server.port",
        port,
    ]
    return subprocess.call(command, cwd=PROJECT_ROOT, env=env)


if __name__ == "__main__":
    raise SystemExit(main())
