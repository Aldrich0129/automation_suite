"""
Router de Telemetría - Automation Suite Backend
================================================

Endpoints para ingestión de eventos de telemetría.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import UsageEvent, App
from app.schemas import TelemetryEvent, TelemetryResponse
from app.config import settings

router = APIRouter()


# ===========================
# Dependencias
# ===========================

async def verify_telemetry_token(
    x_telemetry_token: Optional[str] = Header(None)
):
    """
    Verifica el token de telemetría si está configurado.

    Args:
        x_telemetry_token: Token en header

    Raises:
        HTTPException: Si el token es inválido
    """
    if settings.TELEMETRY_TOKEN:
        if not x_telemetry_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de telemetría requerido"
            )

        if x_telemetry_token != settings.TELEMETRY_TOKEN:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de telemetría inválido"
            )


# ===========================
# Endpoints
# ===========================

@router.post("/telemetry", response_model=TelemetryResponse, tags=["telemetry"])
async def ingest_telemetry(
    event: TelemetryEvent,
    db: AsyncSession = Depends(get_db),
    _token_verified: None = Depends(verify_telemetry_token)
):
    """
    Ingesta un evento de telemetría.

    Args:
        event: Datos del evento

    Returns:
        Confirmación con ID del evento creado
    """
    # Verificar que la app existe
    stmt = select(App).where(App.id == event.app_id)
    result = await db.execute(stmt)
    app = result.scalar_one_or_none()

    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aplicación '{event.app_id}' no encontrada"
        )

    # Crear evento
    usage_event = UsageEvent(
        app_id=event.app_id,
        event_type=event.event_type,
        user_id=event.user_id,
        meta=event.meta
    )

    db.add(usage_event)
    await db.commit()
    await db.refresh(usage_event)

    return TelemetryResponse(
        status="ok",
        event_id=usage_event.id
    )
