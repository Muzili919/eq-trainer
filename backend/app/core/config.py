from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "EQ Trainer"
    debug: bool = False

    database_url: str = "sqlite:///./eq_trainer.db"

    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    deepseek_model: str = "deepseek-chat"

    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 30

    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]


settings = Settings()

if not settings.jwt_secret:
    raise RuntimeError("JWT_SECRET must be set in .env or environment variable")
