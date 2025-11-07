"""
Router de Estadísticas - Automation Suite Backend
==================================================

Endpoints para consultar métricas y estadísticas de uso.
"""

from typing import Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Cookie, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import UsageEvent, App
from app.schemas import StatsSummary, AppStats, EventCount, AppTimeSeries, TimeSeriesPoint
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
# Endpoints de Estadísticas
# ===========================

@router.get("/admin/stats/summary", response_model=StatsSummary, tags=["admin"])
async def get_stats_summary(
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Obtiene resumen de estadísticas por app y tipo de evento.

    Args:
        days: Número de días a considerar (default: 30)

    Returns:
        Resumen con totales por app y tipo de evento
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    # Obtener todas las apps
    stmt_apps = select(App)
    result_apps = await db.execute(stmt_apps)
    apps = result_apps.scalars().all()

    apps_stats = []
    total_events = 0

    for app in apps:
        # Contar eventos por tipo para esta app
        stmt_events = (
            select(
                UsageEvent.event_type,
                func.count(UsageEvent.id).label("count")
            )
            .where(UsageEvent.app_id == app.id)
            .where(UsageEvent.created_at >= cutoff_date)
            .group_by(UsageEvent.event_type)
        )

        result_events = await db.execute(stmt_events)
        events_by_type = result_events.all()

        event_counts = [
            EventCount(event_type=row[0], count=row[1])
            for row in events_by_type
        ]

        app_total = sum(ec.count for ec in event_counts)
        total_events += app_total

        if event_counts:  # Solo incluir apps con eventos
            apps_stats.append(AppStats(
                app_id=app.id,
                app_name=app.name,
                events=event_counts,
                total_events=app_total
            ))

    return StatsSummary(
        apps=apps_stats,
        total_events=total_events,
        days=days
    )


@router.get("/admin/stats/app/{app_id}", response_model=AppTimeSeries, tags=["admin"])
async def get_app_time_series(
    app_id: str,
    event_type: str = Query(default="generate_document"),
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Obtiene serie temporal de eventos para una aplicación.

    Args:
        app_id: ID de la aplicación
        event_type: Tipo de evento (default: generate_document)
        days: Número de días a considerar (default: 30)

    Returns:
        Serie temporal diaria
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

    cutoff_date = datetime.utcnow() - timedelta(days=days)

    # Contar eventos por día
    stmt_events = (
        select(
            func.date(UsageEvent.created_at).label("date"),
            func.count(UsageEvent.id).label("count")
        )
        .where(UsageEvent.app_id == app_id)
        .where(UsageEvent.event_type == event_type)
        .where(UsageEvent.created_at >= cutoff_date)
        .group_by(func.date(UsageEvent.created_at))
        .order_by(func.date(UsageEvent.created_at))
    )

    result_events = await db.execute(stmt_events)
    events_by_day = result_events.all()

    # Crear diccionario con los datos
    events_dict = {str(row[0]): row[1] for row in events_by_day}

    # Generar serie completa (rellenar días sin datos con 0)
    series = []
    current_date = cutoff_date.date()
    end_date = datetime.utcnow().date()

    while current_date <= end_date:
        date_str = current_date.isoformat()
        count = events_dict.get(date_str, 0)
        series.append(TimeSeriesPoint(date=date_str, count=count))
        current_date += timedelta(days=1)

    return AppTimeSeries(
        app_id=app.id,
        app_name=app.name,
        event_type=event_type,
        series=series
    )
