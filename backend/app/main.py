from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.requests import Request

from app.api.v1.router import api_router
from app.db.init_db import init_db
from app.i18n.exceptions import I18nHTTPException
from app.i18n.resolver import resolve_locale, t
from app.security.auth import decode_access_token

app = FastAPI(title="MES Lite", version="0.1.0")


@app.on_event("startup")
def startup_init_db() -> None:
    init_db()


@app.middleware("http")
async def auth_identity_middleware(request: Request, call_next):
    auth_header = request.headers.get("Authorization")
    request.state.auth_identity = None

    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.removeprefix("Bearer ").strip()
        request.state.auth_identity = decode_access_token(token)

    return await call_next(request)


app.include_router(api_router)


@app.exception_handler(I18nHTTPException)
async def i18n_exception_handler(request: Request, exc: I18nHTTPException) -> JSONResponse:
    """Return structured { error_code, message } for i18n-aware exceptions."""
    locale = resolve_locale(request)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "message": t(exc.error_code, locale),
        },
        headers=exc.headers,
    )


@app.get("/health")
def health():
    return {"status": "ok"}
