from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Workflow IA Service"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8001

    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash"

    ai_provider: str = "gemini"
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


settings = Settings()
