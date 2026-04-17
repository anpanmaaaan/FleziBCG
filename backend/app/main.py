from fastapi import FastAPI
from starlette.requests import Request

from app.api.v1.router import api_router
from app.db.init_db import init_db
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


@app.get("/health")
def health():
    return {"status": "ok"}
