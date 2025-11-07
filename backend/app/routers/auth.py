"""
Router de Autenticación - Automation Suite Backend
===================================================

Endpoints para login y logout de administradores.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.schemas import AdminLogin, LoginResponse, MessageResponse, AdminUserOut
from app.services.auth_service import authenticate_admin
from app.auth.session import create_session, verify_session

router = APIRouter()


@router.post("/admin/login", response_model=LoginResponse, tags=["admin"])
async def login(
    credentials: AdminLogin,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Inicia sesión de administrador.

    Args:
        credentials: Usuario y contraseña
        response: Response para establecer cookie

    Returns:
        Información del usuario autenticado
    """
    user = await authenticate_admin(
        db,
        credentials.username,
        credentials.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )

    # Crear sesión
    session_token = create_session(user.username, user.id)

    # Establecer cookie HttpOnly
    response.set_cookie(
        key="admin_session",
        value=session_token,
        httponly=True,
        secure=False,  # Cambiar a True en producción con HTTPS
        samesite="lax",
        max_age=28800  # 8 horas
    )

    return LoginResponse(
        status="ok",
        user=AdminUserOut.model_validate(user)
    )


@router.post("/admin/logout", response_model=MessageResponse, tags=["admin"])
async def logout(response: Response):
    """
    Cierra sesión de administrador.

    Args:
        response: Response para eliminar cookie

    Returns:
        Mensaje de confirmación
    """
    # Eliminar cookie
    response.delete_cookie(key="admin_session")

    return MessageResponse(message="Sesión cerrada correctamente")


@router.get("/admin/me", response_model=AdminUserOut, tags=["admin"])
async def get_current_user(
    session: Optional[str] = Cookie(None, alias="admin_session")
):
    """
    Obtiene información del usuario autenticado.

    Args:
        session: Cookie de sesión

    Returns:
        Información del usuario
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

    # Retornar datos básicos (sin consultar BD)
    return AdminUserOut(
        id=session_data["user_id"],
        username=session_data["username"],
        created_at=None,  # No disponible en sesión
        last_login=None
    )
