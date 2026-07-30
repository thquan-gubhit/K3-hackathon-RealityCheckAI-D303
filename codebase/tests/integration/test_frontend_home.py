"""Streamlit Home page integration tests."""

from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

from frontend import api_client


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_home_page_reports_connected_backend(monkeypatch) -> None:
    """The page executes cleanly and renders a successful backend check."""

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def getcode(self):
            return 200

        def read(self):
            return (
                b'{"status":"ok","app_name":"Adaptive Learning System",'
                b'"environment":"test","database":"configured"}'
            )

    monkeypatch.setenv("BACKEND_API_URL", "http://backend.invalid")
    monkeypatch.setattr(api_client, "urlopen", lambda *args, **kwargs: FakeResponse())

    app = AppTest.from_file(PROJECT_ROOT / "frontend" / "Home.py").run(timeout=10)

    assert not app.exception
    assert [item.value for item in app.title] == ["Adaptive Learning System"]
    assert [item.value for item in app.success] == ["Backend is online."]
