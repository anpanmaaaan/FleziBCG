from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "mes-lite"
    app_env: str = "dev"
    debug: bool = True
    database_url: str = "postgresql+psycopg://mes:mes@localhost:5432/mes"
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()