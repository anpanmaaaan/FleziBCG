from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "mes-lite"
    app_env: str = "dev"
    debug: bool = True
    database_url: str = "postgresql+psycopg://mes:mes@localhost:5432/mes"
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 480
    auth_default_users_json: str = (
        '[{"user_id":"u-demo","username":"demo","email":"demo@mes.local",'
        '"password":"demo123","tenant_id":"default","role_code":"SUPERVISOR"}]'
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()