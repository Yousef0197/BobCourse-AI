from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Application
    APP_ENV: str = "development"
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql://bobcourse:bobcourse@localhost:5432/bobcourse_db"

    # Security
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Java Analytics Service
    ANALYTICS_SERVICE_URL: str = "http://localhost:8080"

    # AI Provider
    AI_PROVIDER: str = "offline"
    OPENAI_API_KEY: str = ""

    # Anonymity
    MIN_RESPONSES_THRESHOLD: int = 5

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173"]


settings = Settings()
