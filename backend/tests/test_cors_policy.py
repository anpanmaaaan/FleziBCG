from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import apply_cors_middleware


def _test_app() -> FastAPI:
    app = FastAPI()
    apply_cors_middleware(app)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


def test_preflight_allows_configured_origin() -> None:
    client = TestClient(_test_app())
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization,Content-Type",
        },
    )

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert response.headers.get("access-control-allow-credentials") == "true"


def test_preflight_rejects_unlisted_origin() -> None:
    client = TestClient(_test_app())
    response = client.options(
        "/health",
        headers={
            "Origin": "https://evil.example",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 400
    assert response.headers.get("access-control-allow-origin") is None
