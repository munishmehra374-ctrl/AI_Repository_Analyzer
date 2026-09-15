from functools import lru_cache

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):

    # ==========================================================
    # Project
    # ==========================================================

    PROJECT_NAME: str = (
        "Repository Intelligence Platform"
    )

    LOG_LEVEL: str = "INFO"

    # ==========================================================
    # LLM Configuration
    # ==========================================================

    LLM_PROVIDER: str = "groq"

    GROQ_API_KEY: str 

    GROQ_MODEL: str = (
        "llama-3.3-70b-versatile"
    )

    TEMPERATURE: float = 0.2

    # Maximum output allowed by the provider/model.
    # Individual agents should use smaller budgets below.
    MAX_TOKENS: int = 4096

    # ==========================================================
    # Global Request / Context Budgets
    # ==========================================================

    # Maximum tokens allowed for a single LLM request
    # according to our application-level budget.
    REQUEST_TOKEN_BUDGET: int = 8000

    # Maximum tokens allowed for repository context.
    CONTEXT_TOKEN_BUDGET: int = 4000

    # Output tokens reserved while calculating context.
    OUTPUT_TOKEN_RESERVE: int = 800

    # ==========================================================
    # Per-Agent Output Budgets
    # ==========================================================

    # Planner only needs to return structured routing information.
    PLANNER_MAX_OUTPUT_TOKENS: int = 800

    # Implementation analysis may need more room to explain code.
    ANALYSIS_MAX_OUTPUT_TOKENS: int = 1200

    # Security / architecture findings should remain concise.
    SECURITY_MAX_OUTPUT_TOKENS: int = 1200

    # Reviewer should produce a compact reviewed summary.
    REVIEWER_MAX_OUTPUT_TOKENS: int = 800

    # Final user-facing answer.
    ANSWER_MAX_OUTPUT_TOKENS: int = 800

    # ==========================================================
    # Neo4j
    # ==========================================================

    NEO4J_URI: str
    NEO4J_USERNAME: str
    NEO4J_PASSWORD: str

    # ==========================================================
    # Redis
    # ==========================================================

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # ==========================================================
    # Pydantic Settings
    # ==========================================================

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()