"""
Cliente HTTP - Portal Automation Suite
=======================================

Cliente para consumir el backend REST.
"""

import os
from typing import Dict, List, Optional, Any
from pathlib import Path
import sys

import requests

# Importar configuración
CORE_PATH = Path(__file__).parent.parent.parent / "core"
sys.path.insert(0, str(CORE_PATH))

try:
    from core.settings import get_backend_base_url
except ImportError:
    def get_backend_base_url():
        return os.getenv("BACKEND_BASE_URL", "http://localhost:8601")


class BackendClient:
    """Cliente HTTP para el backend de Automation Suite."""

    def __init__(self, base_url: Optional[str] = None, timeout: int = 10):
        """
        Inicializa el cliente.

        Args:
            base_url: URL base del backend (opcional, lee de env)
            timeout: Timeout en segundos para las requests
        """
        self.base_url = base_url or get_backend_base_url()
        self.timeout = timeout
        self.session = requests.Session()

    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> requests.Response:
        """
        Ejecuta una request HTTP.

        Args:
            method: Método HTTP (GET, POST, etc.)
            endpoint: Endpoint (ej. "/api/apps")
            **kwargs: Argumentos adicionales para requests

        Returns:
            Response object

        Raises:
            requests.RequestException: Si hay error de conexión
        """
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.request(
                method,
                url,
                timeout=self.timeout,
                **kwargs
            )
            return response
        except requests.exceptions.Timeout:
            raise Exception(f"Timeout al conectar con el backend ({self.base_url})")
        except requests.exceptions.ConnectionError:
            raise Exception(f"No se pudo conectar al backend ({self.base_url})")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error en la request: {str(e)}")

    # ===========================
    # Aplicaciones
    # ===========================

    def list_apps(self) -> List[Dict]:
        """
        Lista todas las aplicaciones públicas.

        Returns:
            Lista de aplicaciones
        """
        response = self._request("GET", "/api/apps")
        response.raise_for_status()
        return response.json()

    def list_all_apps(self) -> List[Dict]:
        """
        Lista todas las aplicaciones (admin).

        Returns:
            Lista de aplicaciones
        """
        response = self._request("GET", "/api/admin/apps")
        response.raise_for_status()
        return response.json()

    def create_app(self, app_data: Dict) -> Dict:
        """
        Crea una nueva aplicación (admin).

        Args:
            app_data: Datos de la aplicación

        Returns:
            Aplicación creada
        """
        response = self._request("POST", "/api/admin/apps", json=app_data)
        response.raise_for_status()
        return response.json()

    def update_app(self, app_id: str, app_data: Dict) -> Dict:
        """
        Actualiza una aplicación (admin).

        Args:
            app_id: ID de la aplicación
            app_data: Datos a actualizar

        Returns:
            Aplicación actualizada
        """
        response = self._request("PATCH", f"/api/admin/apps/{app_id}", json=app_data)
        response.raise_for_status()
        return response.json()

    def delete_app(self, app_id: str):
        """
        Elimina una aplicación (admin).

        Args:
            app_id: ID de la aplicación
        """
        response = self._request("DELETE", f"/api/admin/apps/{app_id}")
        response.raise_for_status()

    def set_app_password(self, app_id: str, password: str) -> Dict:
        """
        Establece contraseña de una aplicación (admin).

        Args:
            app_id: ID de la aplicación
            password: Nueva contraseña

        Returns:
            Mensaje de confirmación
        """
        response = self._request(
            "POST",
            f"/api/admin/apps/{app_id}/password",
            json={"password": password}
        )
        response.raise_for_status()
        return response.json()

    def remove_app_password(self, app_id: str) -> Dict:
        """
        Elimina contraseña de una aplicación (admin).

        Args:
            app_id: ID de la aplicación

        Returns:
            Mensaje de confirmación
        """
        response = self._request("DELETE", f"/api/admin/apps/{app_id}/password")
        response.raise_for_status()
        return response.json()

    def check_app_access(self, app_id: str, password: str) -> bool:
        """
        Verifica acceso a una aplicación protegida.

        Args:
            app_id: ID de la aplicación
            password: Contraseña

        Returns:
            True si el acceso es válido
        """
        response = self._request(
            "POST",
            "/api/apps/check-access",
            json={"app_id": app_id, "password": password}
        )
        response.raise_for_status()
        data = response.json()
        return data.get("access_granted", False)

    # ===========================
    # Autenticación
    # ===========================

    def login(self, username: str, password: str) -> Dict:
        """
        Inicia sesión como administrador.

        Args:
            username: Nombre de usuario
            password: Contraseña

        Returns:
            Datos del usuario autenticado
        """
        response = self._request(
            "POST",
            "/api/admin/login",
            json={"username": username, "password": password}
        )
        response.raise_for_status()
        return response.json()

    def logout(self):
        """Cierra sesión de administrador."""
        response = self._request("POST", "/api/admin/logout")
        response.raise_for_status()

    def get_current_user(self) -> Optional[Dict]:
        """
        Obtiene información del usuario autenticado.

        Returns:
            Datos del usuario o None si no está autenticado
        """
        try:
            response = self._request("GET", "/api/admin/me")
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        return None

    # ===========================
    # Estadísticas
    # ===========================

    def get_stats_summary(self, days: int = 30) -> Dict:
        """
        Obtiene resumen de estadísticas.

        Args:
            days: Número de días a considerar

        Returns:
            Resumen de estadísticas
        """
        response = self._request("GET", f"/api/admin/stats/summary?days={days}")
        response.raise_for_status()
        return response.json()

    def get_app_time_series(
        self,
        app_id: str,
        event_type: str = "generate_document",
        days: int = 30
    ) -> Dict:
        """
        Obtiene serie temporal de una aplicación.

        Args:
            app_id: ID de la aplicación
            event_type: Tipo de evento
            days: Número de días

        Returns:
            Serie temporal
        """
        response = self._request(
            "GET",
            f"/api/admin/stats/app/{app_id}?event_type={event_type}&days={days}"
        )
        response.raise_for_status()
        return response.json()

    # ===========================
    # Programación
    # ===========================

    def get_app_schedule(self, app_id: str) -> Optional[Dict]:
        """
        Obtiene programación de una aplicación.

        Args:
            app_id: ID de la aplicación

        Returns:
            Programación o None
        """
        response = self._request("GET", f"/api/admin/schedules/{app_id}")
        if response.status_code == 200:
            return response.json()
        return None

    def set_app_schedule(self, app_id: str, schedule_data: Dict) -> Dict:
        """
        Establece programación de una aplicación.

        Args:
            app_id: ID de la aplicación
            schedule_data: Datos de programación

        Returns:
            Programación creada
        """
        response = self._request(
            "POST",
            f"/api/admin/schedules/{app_id}",
            json=schedule_data
        )
        response.raise_for_status()
        return response.json()

    def delete_app_schedule(self, app_id: str):
        """
        Elimina programación de una aplicación.

        Args:
            app_id: ID de la aplicación
        """
        response = self._request("DELETE", f"/api/admin/schedules/{app_id}")
        response.raise_for_status()

    # ===========================
    # Health
    # ===========================

    def health_check(self) -> Dict:
        """
        Verifica estado del backend.

        Returns:
            Estado del servicio
        """
        response = self._request("GET", "/api/healthz")
        response.raise_for_status()
        return response.json()
