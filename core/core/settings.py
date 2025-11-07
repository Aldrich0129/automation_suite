"""
Módulo de Configuración - Core
================================

Este módulo proporciona funciones para leer y gestionar la configuración
global de la suite de automatización.

Las variables se leen desde las variables de entorno del sistema,
con valores por defecto si no están definidas.
"""

import os


def get_backend_base_url() -> str:
    """
    Obtiene la URL base del backend desde las variables de entorno.

    Returns:
        str: URL base del backend. Por defecto: 'http://localhost:8601'

    Example:
        >>> url = get_backend_base_url()
        >>> print(url)
        'http://localhost:8601'
    """
    return os.getenv("BACKEND_BASE_URL", "http://localhost:8601")


def get_portal_base_path() -> str:
    """
    Obtiene la ruta base del portal desde las variables de entorno.

    Esta ruta se usa cuando el portal se ejecuta detrás de un proxy
    o en una subruta específica.

    Returns:
        str: Ruta base del portal. Por defecto: '/portal'

    Example:
        >>> path = get_portal_base_path()
        >>> print(path)
        '/portal'
    """
    return os.getenv("PORTAL_BASE_PATH", "/portal")


def get_env_variable(var_name: str, default_value: str = "") -> str:
    """
    Función genérica para leer una variable de entorno.

    Args:
        var_name (str): Nombre de la variable de entorno
        default_value (str): Valor por defecto si la variable no existe

    Returns:
        str: Valor de la variable de entorno o el valor por defecto

    Example:
        >>> debug = get_env_variable("DEBUG", "false")
        >>> print(debug)
        'false'
    """
    return os.getenv(var_name, default_value)
