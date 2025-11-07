"""
Router de Aplicaciones - Automation Suite Backend
==================================================

Endpoints para gestión de aplicaciones (CRUD).
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Cookie
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import App
from app.schemas import (
    AppCreate, AppUpdate, AppOut, AppPassword,
    AppPasswordCheck, MessageResponse
)
from app.services.auth_service import hash_password, verify_password
from app.services.app_service import get_public_catalog, invalidate_catalog_cache
from app.auth.session import verify_session

router = APIRouter()


# ===========================
# Dependencias
# ===========================

async def get_current_admin(
    session: Optional[str] = Cookie(None, alias="admin_session")
):
    """
    Verifica que el usuario esté autenticado como admin.

    Args:
        session: Cookie de sesión

    Raises:
        HTTPException: Si no está autenticado

    Returns:
        Datos de la sesión
    """
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
# Endpoints Públicos
# ===========================

@router.get("/apps", response_model=List[AppOut], tags=["public"])
async def list_public_apps(db: AsyncSession = Depends(get_db)):
    """
    Lista todas las aplicaciones disponibles públicamente.

    Filtra por enabled=True y ventanas temporales activas.
    """
    apps = await get_public_catalog(db)
    return apps


@router.post("/apps/check-access", tags=["public"])
async def check_app_access(
    data: AppPasswordCheck,
    db: AsyncSession = Depends(get_db)
):
    """
    Verifica el acceso a una aplicación protegida por contraseña.

    Args:
        data: app_id y password

    Returns:
        {access_granted: bool}
    """
    stmt = select(App).where(App.id == data.app_id)
    result = await db.execute(stmt)
    app = result.scalar_one_or_none()

    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aplicación no encontrada"
        )

    if app.access_mode != "password":
        return {"access_granted": True}

    if not app.password_hash:
        return {"access_granted": True}

    access_granted = verify_password(data.password, app.password_hash)

    return {"access_granted": access_granted}


# ===========================
# Endpoints Admin
# ===========================

@router.get("/admin/apps", response_model=List[AppOut], tags=["admin"])
async def list_all_apps(
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Lista todas las aplicaciones (admin).

    Incluye apps deshabilitadas y sin filtros.
    """
    stmt = select(App).order_by(App.created_at.desc())
    result = await db.execute(stmt)
    apps = result.scalars().all()

    apps_out = []
    for app in apps:
        app_out = AppOut.model_validate(app)
        app_out.has_password = app.password_hash is not None
        apps_out.append(app_out)

    return apps_out


@router.post("/admin/apps", response_model=AppOut, status_code=status.HTTP_201_CREATED, tags=["admin"])
async def create_app(
    app_in: AppCreate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Crea una nueva aplicación (admin).

    Args:
        app_in: Datos de la aplicación

    Returns:
        Aplicación creada
    """
    # Verificar que no exista
    stmt = select(App).where(App.id == app_in.id)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una aplicación con id '{app_in.id}'"
        )

    app = App(**app_in.model_dump())
    db.add(app)
    await db.commit()
    await db.refresh(app)

    # Invalidar caché
    invalidate_catalog_cache()

    app_out = AppOut.model_validate(app)
    app_out.has_password = False

    return app_out


@router.patch("/admin/apps/{app_id}", response_model=AppOut, tags=["admin"])
async def update_app(
    app_id: str,
    app_update: AppUpdate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Actualiza una aplicación (admin).

    Args:
        app_id: ID de la aplicación
        app_update: Campos a actualizar

    Returns:
        Aplicación actualizada
    """
    stmt = select(App).where(App.id == app_id)
    result = await db.execute(stmt)
    app = result.scalar_one_or_none()

    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aplicación no encontrada"
        )

    # Actualizar campos
    update_data = app_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(app, field, value)

    await db.commit()
    await db.refresh(app)

    # Invalidar caché
    invalidate_catalog_cache()

    app_out = AppOut.model_validate(app)
    app_out.has_password = app.password_hash is not None

    return app_out


@router.delete("/admin/apps/{app_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["admin"])
async def delete_app(
    app_id: str,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Elimina una aplicación (admin).

    Args:
        app_id: ID de la aplicación
    """
    stmt = delete(App).where(App.id == app_id)
    result = await db.execute(stmt)

    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aplicación no encontrada"
        )

    await db.commit()

    # Invalidar caché
    invalidate_catalog_cache()


@router.post("/admin/apps/{app_id}/password", response_model=MessageResponse, tags=["admin"])
async def set_app_password(
    app_id: str,
    password_data: AppPassword,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Establece o actualiza la contraseña de una aplicación (admin).

    Args:
        app_id: ID de la aplicación
        password_data: Nueva contraseña

    Returns:
        Mensaje de confirmación
    """
    stmt = select(App).where(App.id == app_id)
    result = await db.execute(stmt)
    app = result.scalar_one_or_none()

    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aplicación no encontrada"
        )

    # Hash de la contraseña
    app.password_hash = hash_password(password_data.password)

    # Si no está en modo password, cambiarlo
    if app.access_mode != "password":
        app.access_mode = "password"

    await db.commit()

    # Invalidar caché
    invalidate_catalog_cache()

    return MessageResponse(message="Contraseña actualizada correctamente")


@router.delete("/admin/apps/{app_id}/password", response_model=MessageResponse, tags=["admin"])
async def remove_app_password(
    app_id: str,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Elimina la contraseña de una aplicación (admin).

    Args:
        app_id: ID de la aplicación

    Returns:
        Mensaje de confirmación
    """
    stmt = select(App).where(App.id == app_id)
    result = await db.execute(stmt)
    app = result.scalar_one_or_none()

    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aplicación no encontrada"
        )

    app.password_hash = None

    # Cambiar a modo público
    if app.access_mode == "password":
        app.access_mode = "public"

    await db.commit()

    # Invalidar caché
    invalidate_catalog_cache()

    return MessageResponse(message="Contraseña eliminada correctamente")
