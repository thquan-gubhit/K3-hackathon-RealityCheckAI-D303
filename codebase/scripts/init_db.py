"""Initialize the configured database and registered SQLAlchemy tables."""

from __future__ import annotations

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import ConfigurationError, get_settings  # noqa: E402
from app.database import init_db  # noqa: E402


def main() -> int:
    """Validate configuration, initialize storage, and report the result."""

    settings = get_settings()
    try:
        settings.validate_runtime_requirements()
    except ConfigurationError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    init_db()
    print("Database initialized successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
