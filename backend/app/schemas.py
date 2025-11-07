"""
Esquemas Pydantic - Automation Suite Backend
=============================================

Define los esquemas de validación y serialización de datos.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, field_validator


# ===========================
# Esquemas de Aplicación
# ===========================

class AppBase(BaseModel):
    """Esquema base de aplicación."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    path: str = Field(..., min_length=1, max_length=500)
    tags: Optional[str] = None
    enabled: bool = True
    access_mode: str = Field(default="public", pattern="^(public|password|sso)$")
    rate_limit_per_min: Optional[int] = Field(default=None, ge=1)


class AppCreate(AppBase):
    """Esquema para crear una aplicación."""
    id: str = Field(..., min_length=1, max_length=100)


class AppUpdate(BaseModel):
    """Esquema para actualizar una aplicación."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    path: Optional[str] = Field(None, min_length=1, max_length=500)
    tags: Optional[str] = None
    enabled: Optional[bool] = None
    access_mode: Optional[str] = Field(None, pattern="^(public|password|sso)$")
    rate_limit_per_min: Optional[int] = Field(None, ge=1)


class AppOut(AppBase):
    """Esquema de salida de aplicación."""
    id: str
    created_at: datetime
    updated_at: datetime
    has_password: bool = False

    class Config:
        from_attributes = True


class AppPassword(BaseModel):
    """Esquema para establecer contraseña de aplicación."""
    password: str = Field(..., min_length=4)


class AppPasswordCheck(BaseModel):
    """Esquema para verificar contraseña de aplicación."""
    app_id: str
    password: str


# ===========================
# Esquemas de Programación
# ===========================

class AppScheduleBase(BaseModel):
    """Esquema base de programación."""
    enabled_from: Optional[datetime] = None
    enabled_until: Optional[datetime] = None
    cron_expr: Optional[str] = None


class AppScheduleCreate(AppScheduleBase):
    """Esquema para crear programación."""
    pass


class AppScheduleOut(AppScheduleBase):
    """Esquema de salida de programación."""
    id: int
    app_id: str

    class Config:
        from_attributes = True


# ===========================
# Esquemas de Telemetría
# ===========================

class TelemetryEvent(BaseModel):
    """Esquema para evento de telemetría."""
    app_id: str = Field(..., min_length=1)
    event_type: str = Field(..., pattern="^(open|generate_document|error|custom)$")
    user_id: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None


class TelemetryResponse(BaseModel):
    """Respuesta de ingesta de telemetría."""
    status: str = "ok"
    event_id: int


# ===========================
# Esquemas de Estadísticas
# ===========================

class EventCount(BaseModel):
    """Conteo de eventos por tipo."""
    event_type: str
    count: int


class AppStats(BaseModel):
    """Estadísticas por aplicación."""
    app_id: str
    app_name: str
    events: List[EventCount]
    total_events: int


class StatsSummary(BaseModel):
    """Resumen de estadísticas globales."""
    apps: List[AppStats]
    total_events: int
    days: int


class TimeSeriesPoint(BaseModel):
    """Punto en serie temporal."""
    date: str  # YYYY-MM-DD
    count: int


class AppTimeSeries(BaseModel):
    """Serie temporal de una aplicación."""
    app_id: str
    app_name: str
    event_type: str
    series: List[TimeSeriesPoint]


# ===========================
# Esquemas de Autenticación
# ===========================

class AdminLogin(BaseModel):
    """Esquema de login de administrador."""
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=3)


class AdminUserOut(BaseModel):
    """Esquema de salida de usuario administrador."""
    id: int
    username: str
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """Respuesta de login exitoso."""
    status: str = "ok"
    user: AdminUserOut


# ===========================
# Esquemas Generales
# ===========================

class HealthResponse(BaseModel):
    """Respuesta de health check."""
    status: str = "ok"
    version: str = "2.0.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Respuesta de error."""
    detail: str


class MessageResponse(BaseModel):
    """Respuesta genérica con mensaje."""
    message: str
