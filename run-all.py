#!/usr/bin/env python
"""Chạy cả backend lẫn giao diện bằng một lệnh.

    python run-all.py

  Backend  ->  http://127.0.0.1:8000   (FastAPI, adaptive-learning-system)
  Giao diện->  http://127.0.0.1:8899   (prototype Nói Lại Đi)

Ctrl+C một lần là tắt cả hai.

Script tự lo mấy chỗ dễ vấp:
  - Thiếu .env hoặc LLM_API_KEY  -> báo rõ, không để backend chết câm lặng.
  - app.db rỗng                  -> tự chạy init_db, nếu không mọi request 500.
  - Giao diện phải chạy qua http -> PDF.js cần worker, mở bằng file:// là hỏng.
"""

from __future__ import annotations

import http.server
import os
import socket
import socketserver
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

# Console Windows mặc định là cp1252, không in được tiếng Việt -> ép UTF-8.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "adaptive-learning-system"
FRONTEND_DIR = ROOT / "codebase" / "noi-lai-di"
BACKEND_PORT = 8000
FRONTEND_PORT = 8899

C_OK, C_WARN, C_ERR, C_DIM, C_END = "\033[92m", "\033[93m", "\033[91m", "\033[90m", "\033[0m"


def say(tag: str, msg: str, colour: str = "") -> None:
    print(f"{colour}[{tag}]{C_END} {msg}", flush=True)


def port_busy(port: int) -> bool:
    with socket.socket() as probe:
        probe.settimeout(0.4)
        return probe.connect_ex(("127.0.0.1", port)) == 0


def check_env() -> bool:
    """Backend từ chối khởi động nếu thiếu khoá — bắt lỗi ở đây cho rõ ràng."""

    env_file = BACKEND_DIR / ".env"
    if not env_file.exists():
        example = BACKEND_DIR / ".env.example"
        if example.exists():
            env_file.write_text(example.read_text(encoding="utf-8"), encoding="utf-8")
            say("env", f"Đã tạo {env_file.relative_to(ROOT)} từ .env.example", C_WARN)
        else:
            say("env", "Không thấy .env lẫn .env.example", C_ERR)
            return False

    values = {}
    for line in env_file.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip()

    missing = [k for k in ("LLM_API_KEY", "LLM_BASE_URL", "LLM_MODEL") if not values.get(k)]
    if missing:
        say("env", f"Thiếu {', '.join(missing)} trong .env", C_ERR)
        print(f"""
  Mở file này rồi điền:
      {env_file}

      LLM_API_KEY=<khoá của bạn>
      LLM_BASE_URL=https://api.openai.com/v1
      LLM_MODEL=gpt-4o-mini

  Dùng Gemini thì đổi:
      LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
      LLM_MODEL=gemini-2.0-flash

  File .env đã nằm trong .gitignore, không lên GitHub được.
""")
        return False

    say("env", "Cấu hình đủ", C_OK)
    return True


def ensure_database() -> None:
    """app.db rỗng thì mọi request trả 500 DATABASE_ERROR — lỗi rất khó đoán."""

    db = BACKEND_DIR / "data" / "app.db"
    if db.exists() and db.stat().st_size > 0:
        say("db", "Database sẵn sàng", C_OK)
        return

    say("db", "Database chưa có bảng — đang khởi tạo…", C_WARN)
    result = subprocess.run(
        [sys.executable, "scripts/init_db.py"],
        cwd=BACKEND_DIR,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        say("db", "Khởi tạo xong", C_OK)
    else:
        say("db", f"Khởi tạo lỗi: {result.stderr.strip()[:200]}", C_ERR)


def start_backend() -> subprocess.Popen | None:
    if port_busy(BACKEND_PORT):
        say("backend", f"Cổng {BACKEND_PORT} đã có thứ gì đó chạy — dùng luôn", C_WARN)
        return None

    say("backend", f"Đang khởi động trên :{BACKEND_PORT}…", C_DIM)
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app",
         "--host", "127.0.0.1", "--port", str(BACKEND_PORT)],
        cwd=BACKEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    def pump() -> None:
        for line in process.stdout or []:
            line = line.rstrip()
            if not line:
                continue
            if "ERROR" in line or "Traceback" in line:
                say("backend", line[:170], C_ERR)
            elif "Application startup complete" in line:
                say("backend", "Sẵn sàng", C_OK)

    threading.Thread(target=pump, daemon=True).start()

    for _ in range(40):
        if port_busy(BACKEND_PORT):
            return process
        if process.poll() is not None:
            say("backend", "Chết ngay khi khởi động — xem log phía trên", C_ERR)
            return process
        time.sleep(0.5)

    say("backend", "Quá 20 giây chưa lên", C_WARN)
    return process


def start_frontend() -> socketserver.TCPServer | None:
    if port_busy(FRONTEND_PORT):
        say("frontend", f"Cổng {FRONTEND_PORT} đã bận — dùng luôn", C_WARN)
        return None

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)

        def log_message(self, *args):  # im lặng, đỡ rác terminal
            pass

    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer(("127.0.0.1", FRONTEND_PORT), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    say("frontend", f"Phục vụ {FRONTEND_DIR.name}/ trên :{FRONTEND_PORT}", C_OK)
    return server


def main() -> int:
    print()
    say("run", "Khởi động Reality Check AI", C_OK)

    for path, label in ((BACKEND_DIR, "adaptive-learning-system"),
                        (FRONTEND_DIR, "codebase/noi-lai-di")):
        if not path.exists():
            say("run", f"Không thấy thư mục {label}", C_ERR)
            return 1

    backend_ready = check_env()
    if backend_ready:
        ensure_database()

    backend = start_backend() if backend_ready else None
    if not backend_ready:
        say("backend", "Bỏ qua backend. Giao diện vẫn chạy, chấm bằng luật cục bộ.", C_WARN)

    frontend = start_frontend()

    url = f"http://127.0.0.1:{FRONTEND_PORT}/"
    print()
    print("  " + "─" * 56)
    print(f"   Giao diện   {url}")
    print(f"   Backend     http://127.0.0.1:{BACKEND_PORT}"
          f"{'' if backend_ready else '   (tắt)'}")
    print("  " + "─" * 56)
    print(f"{C_DIM}   Ctrl+C để tắt cả hai.")
    print("   Mở bằng http, đừng bấm đúp index.html — PDF.js cần worker.")
    print(f"   Sửa code backend xong phải chạy lại script này.{C_END}")
    print()

    try:
        webbrowser.open(url)
    except Exception:
        pass

    try:
        while True:
            time.sleep(1)
            if backend is not None and backend.poll() is not None:
                say("backend", "Đã dừng", C_WARN)
                backend = None
    except KeyboardInterrupt:
        print()
        say("run", "Đang tắt…", C_DIM)

    if frontend is not None:
        frontend.shutdown()
    if backend is not None:
        backend.terminate()
        try:
            backend.wait(timeout=5)
        except subprocess.TimeoutExpired:
            backend.kill()
    say("run", "Đã tắt cả hai", C_OK)
    return 0


if __name__ == "__main__":
    os.system("")  # bật màu ANSI trên terminal Windows
    sys.exit(main())
