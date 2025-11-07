"""
Router de Programación - Automation Suite Backend
==================================================

Endpoints para gestionar ventanas temporales de aplicaciones.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Cookie
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import App, AppSchedule
from app.schemas import AppScheduleCreate, AppScheduleOut, MessageResponse
from app.services.app_service import invalidate_catalog_cache
from app.auth.session import verify_session

router = APIRouter()


# ===========================
# Dependencias
# ===========================

async def get_current_admin(
    session: Optional[str] = Cookie(None, alias="admin_session")
):
    """Verifica autenticación admin."""
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado"
        )

    session_data = verify_session(session)

    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión inválida o expirada"
        )

    return session_data


# ===========================
# Endpoints
# ===========================

@router.get("/admin/schedules/{app_id}", response_model=Optional[AppScheduleOut], tags=["admin"])
async def get_app_schedule(
    app_id: str,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Obtiene la programación de una aplicación.

    Args:
        app_id: ID de la aplicación

    Returns:
        Programación o None si no existe
    """
    # Verificar que la app existe
    stmt_app = select(App).where(App.id == app_id)
    result_app = await db.execute(stmt_app)
    app = result_app.scalar_one_or_none()

    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aplicación no encontrada"
        )

    # Obtener programación
    stmt = select(AppSchedule).where(AppSchedule.app_id == app_id)
    result = await db.execute(stmt)
    schedule = result.scalar_one_or_none()

    return schedule


@router.post("/admin/schedules/{app_id}", response_model=AppScheduleOut, tags=["admin"])
async def create_or_update_schedule(
    app_id: str,
    schedule_data: AppScheduleCreate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Crea o actualiza la programación de una aplicación.

    Args:
        app_id: ID de la aplicación
        schedule_data: Datos de la programación

    Returns:
        Programación creada o actualizada
    """
    # Verificar que la app existe
    stmt_app = select(App).where(App.id == app_id)
    result_app = await db.execute(stmt_app)
    app = result_app.scalar_one_or_none()

    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aplicación no encontrada"
        )

    # Buscar programación existente
    stmt = select(AppSchedule).where(AppSchedule.app_id == app_id)
    result = await db.execute(stmt)
    schedule = result.scalar_one_or_none()

    if schedule:
        # Actualizar
        schedule.enabled_from = schedule_data.enabled_from
        schedule.enabled_until = schedule_data.enabled_until
        schedule.cron_expr = schedule_data.cron_expr
    else:
        # Crear nueva
        schedule = AppSchedule(
            app_id=app_id,
            **schedule_data.model_dump()
        )
        db.add(schedule)

    await db.commit()
    await db.refresh(schedule)

    # Invalidar caché
    invalidate_catalog_cache()

    return schedule


@router.delete("/admin/schedules/{app_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["admin"])
async def delete_schedule(
    app_id: str,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Elimina la programación de una aplicación.

    Args:
        app_id: ID de la aplicación
    """
    stmt = delete(AppSchedule).where(AppSchedule.app_id == app_id)
    result = await db.execute(stmt)

    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró programación para esta aplicación"
        )

    await db.commit()

    # Invalidar caché
    invalidate_catalog_cache()
