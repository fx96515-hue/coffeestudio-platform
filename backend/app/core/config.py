from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Required settings that must come from environment
    DATABASE_URL: str = Field(default="", min_length=1)
    REDIS_URL: str = Field(default="", min_length=1)
    JWT_SECRET: str = Field(default="", min_length=1)
    JWT_ISSUER: str = "coffeestudio"
    JWT_AUDIENCE: str = "coffeestudio-web"
    CORS_ORIGINS: str = "http://localhost:3000"
    TZ: str = "Europe/Berlin"

    # Dev bootstrap (only used by /auth/dev/bootstrap)
    # Must be a *valid* email (no .local/.test special-use).
    BOOTSTRAP_ADMIN_EMAIL: str = "admin@coffeestudio.com"
    # Intentionally no baked-in default password (fail-fast if missing).
    BOOTSTRAP_ADMIN_PASSWORD: str | None = None

    # --- Perplexity (Sonar) API ---
    # Docs: https://docs.perplexity.ai/
    PERPLEXITY_API_KEY: str | None = None
    PERPLEXITY_BASE_URL: str = "https://api.perplexity.ai"
    # For discovery tasks we prefer models with web/search + structured outputs
    PERPLEXITY_MODEL_DISCOVERY: str = "sonar-pro"
    PERPLEXITY_TIMEOUT_SECONDS: int = 60

    # --- Data freshness defaults (days) ---
    KOOPS_STALE_DAYS: int = 60
    ROESTER_STALE_DAYS: int = 90
    NEWS_STALE_DAYS: int = 2
    FX_STALE_DAYS: int = 2

    # --- Scheduled refresh times (Europe/Berlin) ---
    # Format: "HH:MM,HH:MM,HH:MM"
    NEWS_REFRESH_TIMES: str = "07:30,14:00,20:00"
    MARKET_REFRESH_TIMES: str = "07:30,14:00,20:00"

    # Data Pipeline settings
    DATA_PIPELINE_CIRCUIT_BREAKER_THRESHOLD: int = 3
    DATA_PIPELINE_CIRCUIT_BREAKER_TIMEOUT_S: int = 300
    DATA_PIPELINE_MAX_RETRIES: int = 3

    # Intelligence refresh schedule
    INTELLIGENCE_REFRESH_TIMES: str = "06:00,12:00,18:00,00:00"
    AUTO_ENRICH_TIME: str = "03:00"

    # --- OpenAI for semantic search embeddings ---
    OPENAI_API_KEY: str | None = None
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # --- RAG AI Analyst (Multi-Provider) ---
    RAG_PROVIDER: str = "ollama"  # ollama | openai | groq
    RAG_LLM_MODEL: str = "llama3.1:8b"  # Provider-specific model
    RAG_EMBEDDING_PROVIDER: str = "openai"  # Separate from LLM provider
    RAG_EMBEDDING_MODEL: str = "text-embedding-3-small"  # Or "nomic-embed-text" for Ollama
    RAG_MAX_CONTEXT_ENTITIES: int = 10
    RAG_MAX_CONVERSATION_HISTORY: int = 20
    RAG_TEMPERATURE: float = 0.3

    # --- Ollama (local LLM server) ---
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # --- Groq (optional cloud provider) ---
    GROQ_API_KEY: str | None = None

    def cors_origins_list(self) -> List[str]:
        return [s.strip() for s in self.CORS_ORIGINS.split(",") if s.strip()]

    def refresh_times_list(self, raw: str) -> list[tuple[int, int]]:
        out: list[tuple[int, int]] = []
        for part in (raw or "").split(","):
            part = part.strip()
            if not part:
                continue
            hh, mm = part.split(":")
            out.append((int(hh), int(mm)))
        return out


settings = Settings()
