import sys
from pathlib import Path

# Đưa thư mục gốc của dự án vào Python Path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.database import init_db, engine

if __name__ == "__main__":
    print("Initializing SQLite Database...")
    init_db()
    print("Database initialization complete! Data tables are ready.")
