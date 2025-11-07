"""
Módulo Core - Automation Suite
================================

Este módulo contiene la lógica común y utilidades compartidas
entre todas las aplicaciones de la suite de automatización.

Incluye:
- Configuración general (settings)
- Utilidades comunes
- Funciones reutilizables
"""

from .settings import get_backend_base_url, get_portal_base_path

__version__ = "0.1.0"

__all__ = [
    "get_backend_base_url",
    "get_portal_base_path",
]
