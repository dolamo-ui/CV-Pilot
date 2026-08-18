from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    GROQ_API_KEY: str
    GROQ_MODEL: str = "openai/gpt-oss-120b"

    BACKEND_API_KEY: str

    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def validate(self) -> None:
        if not self.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is missing.")

        if not self.GROQ_API_KEY.startswith("gsk_"):
            raise ValueError(
                "GROQ_API_KEY does not appear to be a valid Groq key."
            )

        if not self.BACKEND_API_KEY or len(self.BACKEND_API_KEY) < 16:
            raise ValueError(
                "BACKEND_API_KEY is missing or too short (use at least 16 "
                "random characters)."
            )


settings = Settings()