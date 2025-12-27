import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    REDIS_URL: str
    JWT_SECRET: str
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
settings = Settings(
    DATABASE_URL=os.getenv("DATABASE_URL", "postgresql+psycopg://coffeestudio:coffeestudio@db:5432/coffeestudio"),
    REDIS_URL=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    JWT_SECRET=os.getenv("JWT_SECRET", "change_me_in_env"),
)
