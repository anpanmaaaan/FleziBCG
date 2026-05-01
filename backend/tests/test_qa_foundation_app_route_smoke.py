from fastapi.testclient import TestClient

import app.main as main_module


def test_app_import_and_openapi_smoke():
    app = main_module.app

    assert app is not None

    schema = app.openapi()
    paths = schema.get("paths", {})

    assert "/health" in paths
    assert "/api/v1/products" in paths
    assert "/api/v1/security-events" in paths
    assert "/api/v1/auth/login" in paths


def test_health_endpoint_returns_ok(monkeypatch):
    # Keep this a true route smoke while avoiding DB startup dependency.
    monkeypatch.setattr(main_module, "init_db", lambda: None)

    client = TestClient(main_module.app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
