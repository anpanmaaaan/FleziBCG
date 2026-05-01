from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_name: str = "mes-lite"
    app_env: str = "dev"
    debug: bool = True
    database_url: str | None = None
    postgres_db: str = "mes"
    postgres_user: str = "mes"
    postgres_password: str = "mes"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    # SECURITY: Explicit CORS allow-list. Comma-separated origins to avoid
    # wildcard trust in browser clients.
    cors_allow_origins: str = (
        "http://localhost:5173,"
        "http://127.0.0.1:5173,"
        "http://localhost:80,"
        "http://127.0.0.1:80"
    )
    # WHY: "change-me" is a deliberately insecure default so that forgetting to
    # set a real secret in production is immediately obvious (fails auth).
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    # WHY: 480 min (8 h) matches a single factory shift. Tokens expire at shift
    # end, forcing re-auth. Adjust if shift patterns change.
    jwt_access_token_expire_minutes: int = 480
    # WHY: 30-day default for refresh tokens. Long-lived to survive across
    # multiple shifts without forcing re-login. Adjust per security policy.
    jwt_refresh_token_expire_days: int = 30
    # INVARIANT: Max impersonation window must never exceed a single shift to
    # limit blast radius of a compromised admin session.
    impersonation_max_duration_minutes: int = 480
    # WHY: Claim TTL defaults mirror shift duration. claim_max_ttl_minutes is
    # the absolute cap; individual claims use claim_default_ttl_minutes.
    claim_default_ttl_minutes: int = 60
    claim_max_ttl_minutes: int = 480
    # POLICY: Canonical default keeps one active claim per operator within the
    # same station context. Enable only for explicit handover workflows.
    allow_claim_without_release: bool = False
    # EDGE: JSON string (not a list) because env vars are always strings.
    # Parsed at startup by user_service.seed_demo_users(). Must be valid JSON
    # array of user objects with user_id, username, password, tenant_id, role_code.
    auth_default_users_json: str = (
        '[{"user_id":"u-demo","username":"demo","email":"demo@mes.local",'
        '"password":"demo123","tenant_id":"default","role_code":"SUPERVISOR"}]'
    )

    # WHY: Two env_file sources — docker/.env.db for containerized DB creds,
    # backend/.env for local dev overrides. Later files take precedence.
    model_config = SettingsConfigDict(
        env_file=(ROOT_DIR / "docker" / ".env.db", ROOT_DIR / "backend" / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="after")
    def set_database_url(self) -> "Settings":
        if not self.database_url:
            self.database_url = (
                f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            )
        return self

    @property
    def cors_allow_origins_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_allow_origins.split(",")
            if origin.strip()
        ]


settings = Settings()
