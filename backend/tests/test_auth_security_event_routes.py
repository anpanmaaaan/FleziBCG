from fastapi import FastAPI
from fastapi.testclient import TestClient
from datetime import datetime, timezone, timedelta

import app.api.v1.auth as auth_router_module
from app.security.dependencies import RequestIdentity, require_authenticated_identity


def _test_app(identity: RequestIdentity) -> FastAPI:
    app = FastAPI()
    app.include_router(auth_router_module.router)
    app.dependency_overrides[require_authenticated_identity] = lambda: identity
    return app


def test_refresh_records_security_event():
    """POST /auth/refresh with a refresh token body accepts the new contract.

    After P0-A-03B, the /auth/refresh endpoint requires a refresh_token in the request body.
    This test verifies that the endpoint signature has been updated.
    Security event emission is tested comprehensively in test_auth_refresh_token_runtime.py.
    """
    from unittest.mock import MagicMock
    
    app = FastAPI()
    app.include_router(auth_router_module.router)
    
    # Override get_db to return a mock
    def mock_get_db():
        yield MagicMock()
    
    app.dependency_overrides[auth_router_module.get_db] = mock_get_db
    
    client = TestClient(app)
    
    # Old contract: POST /auth/refresh with no body should be rejected
    response_old = client.post(
        "/auth/refresh",
        headers={"X-Tenant-ID": "default"},
    )
    # 422 because no body / invalid request
    assert response_old.status_code in [422, 401, 400]
    
    # New contract: POST /auth/refresh with refresh_token body is required
    response_new = client.post(
        "/auth/refresh",
        json={"refresh_token": "dummy-token"},
        headers={"X-Tenant-ID": "default"},
    )
    # Will be 401 or 500 (depending on mocking), but NOT 422 (schema validation passed)
    assert response_new.status_code != 422
