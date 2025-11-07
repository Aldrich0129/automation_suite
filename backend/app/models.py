"""
Modelos de Base de Datos - Automation Suite Backend
====================================================

Define los modelos de SQLAlchemy para la gestión de aplicaciones,
eventos de uso y usuarios administradores.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer,
    String, Text, JSON, Index
)
from sqlalchemy.orm import relationship

from app.db import Base


class App(Base):
    """
    Modelo de Aplicación.

    Representa una aplicación dentro de la suite de automatización.
    """
    __tablename__ = "apps"

    id = Column(String(100), primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    path = Column(String(500), nullable=False)
    tags = Column(String(500), nullable=True)  # Separado por comas
    enabled = Column(Boolean, default=True, nullable=False, index=True)
    access_mode = Column(
        String(20),
        default="public",
        nullable=False,
        index=True
    )  # public, password, sso
    password_hash = Column(String(200), nullable=True)
    rate_limit_per_min = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relaciones
    schedules = relationship("AppSchedule", back_populates="app", cascade="all, delete-orphan")
    events = relationship("UsageEvent", back_populates="app", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<App(id='{self.id}', name='{self.name}', enabled={self.enabled})>"


class AppSchedule(Base):
    """
    Modelo de Programación de Aplicación.

    Define ventanas temporales de disponibilidad para las aplicaciones.
    """
    __tablename__ = "app_schedules"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    app_id = Column(String(100), ForeignKey("apps.id", ondelete="CASCADE"), nullable=False)
    enabled_from = Column(DateTime, nullable=True)
    enabled_until = Column(DateTime, nullable=True)
    cron_expr = Column(String(100), nullable=True)  # Reservado para futuro

    # Relaciones
    app = relationship("App", back_populates="schedules")

    def __repr__(self):
        return f"<AppSchedule(app_id='{self.app_id}', from={self.enabled_from}, until={self.enabled_until})>"


class UsageEvent(Base):
    """
    Modelo de Evento de Uso.

    Registra eventos de telemetría de las aplicaciones.
    """
    __tablename__ = "usage_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    app_id = Column(String(100), ForeignKey("apps.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(50), nullable=False)  # open, generate_document, error, custom
    user_id = Column(String(200), nullable=True)
    meta = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relaciones
    app = relationship("App", back_populates="events")

    # Índices compuestos
    __table_args__ = (
        Index('ix_usage_events_app_created', 'app_id', 'created_at'),
        Index('ix_usage_events_type_created', 'event_type', 'created_at'),
    )

    def __repr__(self):
        return f"<UsageEvent(app_id='{self.app_id}', type='{self.event_type}', at={self.created_at})>"


class AdminUser(Base):
    """
    Modelo de Usuario Administrador.

    Representa usuarios con acceso al panel de administración.
    """
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<AdminUser(username='{self.username}')>"
