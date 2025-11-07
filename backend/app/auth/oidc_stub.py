"""
OIDC Stub - Automation Suite Backend
=====================================

Stub para futura integración con OpenID Connect.
Este módulo está reservado para implementación futura de SSO.
"""

from typing import Optional, Dict


class OIDCProvider:
    """Stub para proveedor OIDC."""

    def __init__(self, issuer_url: str, client_id: str, client_secret: str):
        """
        Inicializa el proveedor OIDC (stub).

        Args:
            issuer_url: URL del proveedor OIDC
            client_id: ID del cliente
            client_secret: Secret del cliente
        """
        self.issuer_url = issuer_url
        self.client_id = client_id
        self.client_secret = client_secret

    async def get_authorization_url(self, redirect_uri: str, state: str) -> str:
        """
        Genera URL de autorización (stub).

        Args:
            redirect_uri: URI de redirección
            state: Estado para CSRF protection

        Returns:
            URL de autorización
        """
        # TODO: Implementar generación de URL real
        return f"{self.issuer_url}/authorize?client_id={self.client_id}&redirect_uri={redirect_uri}&state={state}"

    async def exchange_code(self, code: str, redirect_uri: str) -> Optional[Dict]:
        """
        Intercambia código de autorización por tokens (stub).

        Args:
            code: Código de autorización
            redirect_uri: URI de redirección

        Returns:
            Diccionario con tokens o None
        """
        # TODO: Implementar intercambio real
        return None

    async def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verifica y decodifica un token JWT (stub).

        Args:
            token: Token JWT

        Returns:
            Claims del token o None
        """
        # TODO: Implementar verificación real
        return None


# Instancia global del proveedor OIDC (desactivada por defecto)
oidc_provider: Optional[OIDCProvider] = None


def init_oidc(issuer_url: str, client_id: str, client_secret: str):
    """
    Inicializa el proveedor OIDC.

    Args:
        issuer_url: URL del proveedor OIDC
        client_id: ID del cliente
        client_secret: Secret del cliente
    """
    global oidc_provider
    oidc_provider = OIDCProvider(issuer_url, client_id, client_secret)
