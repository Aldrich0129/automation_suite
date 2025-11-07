"""
Gestión de Sesiones - Automation Suite Backend
===============================================

Implementa el manejo de sesiones mediante cookies firmadas.
"""

import json
import hmac
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict

from app.config import settings


def sign_data(data: Dict) -> str:
    """
    Firma un diccionario de datos.

    Args:
        data: Datos a firmar

    Returns:
        Cadena firmada en base64
    """
    json_data = json.dumps(data, sort_keys=True)
    signature = hmac.new(
        settings.SECRET_KEY.encode(),
        json_data.encode(),
        hashlib.sha256
    ).hexdigest()

    payload = {"data": data, "signature": signature}
    return base64.b64encode(json.dumps(payload).encode()).decode()


def verify_data(signed_data: str) -> Optional[Dict]:
    """
    Verifica y extrae datos firmados.

    Args:
        signed_data: Cadena firmada en base64

    Returns:
        Datos originales si la firma es válida, None en caso contrario
    """
    try:
        decoded = base64.b64decode(signed_data.encode()).decode()
        payload = json.loads(decoded)

        data = payload.get("data")
        signature = payload.get("signature")

        if not data or not signature:
            return None

        # Verificar firma
        json_data = json.dumps(data, sort_keys=True)
        expected_signature = hmac.new(
            settings.SECRET_KEY.encode(),
            json_data.encode(),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected_signature):
            return None

        return data
    except Exception:
        return None


def create_session(username: str, user_id: int) -> str:
    """
    Crea una sesión firmada.

    Args:
        username: Nombre de usuario
        user_id: ID del usuario

    Returns:
        Token de sesión firmado
    """
    expires_at = datetime.utcnow() + timedelta(hours=settings.SESSION_EXPIRE_HOURS)

    session_data = {
        "username": username,
        "user_id": user_id,
        "expires_at": expires_at.isoformat(),
    }

    return sign_data(session_data)


def verify_session(session_token: str) -> Optional[Dict]:
    """
    Verifica y extrae información de una sesión.

    Args:
        session_token: Token de sesión

    Returns:
        Datos de sesión si es válida, None si expiró o es inválida
    """
    data = verify_data(session_token)

    if not data:
        return None

    # Verificar expiración
    try:
        expires_at = datetime.fromisoformat(data["expires_at"])
        if datetime.utcnow() > expires_at:
            return None
    except (KeyError, ValueError):
        return None

    return data
