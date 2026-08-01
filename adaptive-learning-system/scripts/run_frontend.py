import os
import sys
import subprocess
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
react_dir = root_dir / "react-frontend"

if __name__ == "__main__":
    print("Starting Reality Check AI (Modern React/Vite Frontend)...")
    if not react_dir.exists():
        print(f"Error: Directory {react_dir} does not exist.", file=sys.stderr)
        sys.exit(1)
        
    try:
        subprocess.run(["npm", "run", "dev"], cwd=react_dir, check=True)
    except KeyboardInterrupt:
        print("\nFrontend dev server stopped.")
    except Exception as e:
        print(f"\nError running 'npm run dev' in {react_dir}: {e}", file=sys.stderr)
        sys.exit(1)
