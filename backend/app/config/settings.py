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
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 480
    impersonation_max_duration_minutes: int = 480
    claim_default_ttl_minutes: int = 60
    claim_max_ttl_minutes: int = 480
    auth_default_users_json: str = (
        '[{"user_id":"u-demo","username":"demo","email":"demo@mes.local",'
        '"password":"demo123","tenant_id":"default","role_code":"SUPERVISOR"}]'
    )

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

settings = Settings()