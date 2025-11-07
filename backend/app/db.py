"""
Base de Datos - Automation Suite Backend
=========================================

Configuración de SQLAlchemy para conexiones asíncronas.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.config import settings

# Motor de base de datos asíncrono
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
)

# Fábrica de sesiones asíncronas
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# Base declarativa para los modelos
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Generador de sesiones de base de datos.

    Yields:
        AsyncSession: Sesión de base de datos activa
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    Inicializa la base de datos creando todas las tablas.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
