"""
Servicio de Aplicaciones - Automation Suite Backend
====================================================

Gestiona la lógica de negocio de las aplicaciones.
"""

from typing import List, Optional
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import App, AppSchedule
from app.schemas import AppOut
from app.utils.cache import cache
from app.config import settings


async def get_public_catalog(db: AsyncSession) -> List[AppOut]:
    """
    Obtiene el catálogo público de aplicaciones con caché.

    Filtra por:
    - enabled = True
    - Ventanas temporales activas (si existen)

    Args:
        db: Sesión de base de datos

    Returns:
        Lista de aplicaciones disponibles
    """
    cache_key = "public_catalog"
    cached = cache.get(cache_key)

    if cached is not None:
        return cached

    # Obtener aplicaciones habilitadas con sus programaciones
    stmt = select(App).where(App.enabled == True).options(
        selectinload(App.schedules)
    )
    result = await db.execute(stmt)
    apps = result.scalars().all()

    # Filtrar por ventanas temporales
    now = datetime.utcnow()
    available_apps = []

    for app in apps:
        if is_app_available(app, now):
            app_out = AppOut.model_validate(app)
            app_out.has_password = app.password_hash is not None
            available_apps.append(app_out)

    # Cachear resultado
    cache.set(cache_key, available_apps, settings.CATALOG_CACHE_TTL)

    return available_apps


def is_app_available(app: App, now: Optional[datetime] = None) -> bool:
    """
    Verifica si una aplicación está disponible según su programación.

    Args:
        app: Aplicación a verificar
        now: Timestamp actual (opcional, usa utcnow por defecto)

    Returns:
        True si la app está disponible, False en caso contrario
    """
    if not app.enabled:
        return False

    if not app.schedules:
        return True

    if now is None:
        now = datetime.utcnow()

    for schedule in app.schedules:
        # Si tiene enabled_from y aún no ha llegado, no está disponible
        if schedule.enabled_from and now < schedule.enabled_from:
            return False

        # Si tiene enabled_until y ya pasó, no está disponible
        if schedule.enabled_until and now > schedule.enabled_until:
            return False

    return True


def invalidate_catalog_cache():
    """Invalida el caché del catálogo público."""
    cache.delete("public_catalog")
