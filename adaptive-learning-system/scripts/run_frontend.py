import os
import sys
import subprocess
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

if __name__ == "__main__":
    print("Starting Adaptive Learning System Streamlit Frontend...")
    os.environ["PYTHONPATH"] = str(root_dir)
    streamlit_path = sys.executable
    cmd = [
        streamlit_path,
        "-m", "streamlit", "run",
        str(root_dir / "frontend" / "Home.py"),
        "--server.port", "8501",
        "--server.address", "127.0.0.1"
    ]
    try:
        subprocess.run(cmd, cwd=root_dir, check=True)
    except KeyboardInterrupt:
        print("\nStreamlit application stopped.")
