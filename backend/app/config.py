"""
Configurações centrais da aplicação.
Carrega variáveis de ambiente via pydantic-settings.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ── Aplicação ──────────────────────────────────────────────────────────
    APP_NAME: str = "ClinicAnalytics"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production"

    # ── Banco de dados (Supabase / PostgreSQL) ────────────────────────────
    DATABASE_URL: str          # ex: postgresql://user:pass@host:5432/db
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    # ── CORS ──────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
