"""
Servicio de Autenticación - Automation Suite Backend
=====================================================

Gestiona la autenticación de usuarios administradores.
"""

from typing import Optional
from datetime import datetime

import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AdminUser
from app.config import settings


def hash_password(password: str) -> str:
    """
    Genera un hash bcrypt de una contraseña.

    Args:
        password: Contraseña en texto plano

    Returns:
        Hash bcrypt de la contraseña
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verifica una contraseña contra su hash.

    Args:
        password: Contraseña en texto plano
        password_hash: Hash bcrypt

    Returns:
        True si la contraseña es correcta, False en caso contrario
    """
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except Exception:
        return False


async def authenticate_admin(
    db: AsyncSession,
    username: str,
    password: str
) -> Optional[AdminUser]:
    """
    Autentica un usuario administrador.

    Args:
        db: Sesión de base de datos
        username: Nombre de usuario
        password: Contraseña

    Returns:
        Usuario si las credenciales son válidas, None en caso contrario
    """
    stmt = select(AdminUser).where(AdminUser.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    # Actualizar último login
    user.last_login = datetime.utcnow()
    await db.commit()

    return user


async def create_admin_user(
    db: AsyncSession,
    username: str,
    password: str
) -> AdminUser:
    """
    Crea un nuevo usuario administrador.

    Args:
        db: Sesión de base de datos
        username: Nombre de usuario
        password: Contraseña

    Returns:
        Usuario creado
    """
    password_hash = hash_password(password)

    user = AdminUser(
        username=username,
        password_hash=password_hash
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


async def ensure_default_admin(db: AsyncSession):
    """
    Asegura que exista un usuario administrador por defecto.

    Args:
        db: Sesión de base de datos
    """
    stmt = select(AdminUser)
    result = await db.execute(stmt)
    existing_admins = result.scalars().all()

    if not existing_admins:
        await create_admin_user(
            db,
            settings.ADMIN_DEFAULT_USER,
            settings.ADMIN_DEFAULT_PASS
        )
