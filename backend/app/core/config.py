from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    PROJECT_NAME: str = "Repository Intelligence Platform"

    LOG_LEVEL: str = "INFO"

    LLM_PROVIDER: str = "groq"

    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    TEMPERATURE: float = 0.2
    MAX_TOKENS: int = 4096

    # Neo4j
    NEO4J_URI: str
    NEO4J_USERNAME: str
    NEO4J_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()