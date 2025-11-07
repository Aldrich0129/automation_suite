"""
Configuración del Backend - Automation Suite
============================================

Gestiona la configuración del backend mediante variables de entorno.
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Cargar variables de entorno desde .env
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    """Clase de configuración del backend."""

    # Base de datos
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./automation.db"
    )

    # Seguridad
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change_me_in_production")
    TELEMETRY_TOKEN: Optional[str] = os.getenv("TELEMETRY_TOKEN")

    # Admin por defecto
    ADMIN_DEFAULT_USER: str = os.getenv("ADMIN_DEFAULT_USER", "admin")
    ADMIN_DEFAULT_PASS: str = os.getenv("ADMIN_DEFAULT_PASS", "admin123")

    # CORS
    CORS_ALLOW_ORIGIN: str = os.getenv("CORS_ALLOW_ORIGIN", "http://localhost:8600")

    # Sesión
    SESSION_EXPIRE_HOURS: int = int(os.getenv("SESSION_EXPIRE_HOURS", "8"))

    # Cache
    CATALOG_CACHE_TTL: int = int(os.getenv("CATALOG_CACHE_TTL", "15"))

    # Rate limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

    # Servidor
    HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("BACKEND_PORT", "8601"))

    # Seed
    APPS_REGISTRY_PATH: Optional[str] = os.getenv("APPS_REGISTRY_PATH")


settings = Settings()
