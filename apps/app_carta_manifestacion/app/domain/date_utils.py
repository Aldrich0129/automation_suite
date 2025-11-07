"""
Utilidades de Fechas - App Carta Manifestación
==============================================

Funciones para parsear y formatear fechas.
"""

import locale
from datetime import datetime
from typing import Optional


def set_spanish_locale() -> None:
    """
    Fuerza el locale a español para que %B devuelva «enero, febrero…».
    Probamos varios identificadores según sistema operativo.
    """
    for loc in (
        "es_ES.UTF-8",   # Linux, macOS
        "es_ES.utf8",
        "es_ES",         # Windows ≥10
        "Spanish_Spain", # Windows antiguos
        "Spanish"        # Recurso final
    ):
        try:
            locale.setlocale(locale.LC_TIME, loc)
            break
        except locale.Error:
            continue


def parse_date_string(date_string: Optional[str]) -> datetime:
    """
    Convierte string de fecha a objeto datetime.

    Args:
        date_string: Fecha en formato string

    Returns:
        datetime: Objeto datetime parseado
    """
    if not date_string:
        return datetime.now()

    # Intentar varios formatos de fecha
    formats = [
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d de %B de %Y",
        "%Y/%m/%d",
        "%d.%m.%Y",
        "%Y.%m.%d",
        "%m/%d/%Y",  # Formato americano
        "%Y/%d/%m",  # Año/día/mes
    ]

    # Para manejar nombres de meses en español
    set_spanish_locale()

    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except:
            continue

    # Si no se puede parsear, devolver fecha actual
    return datetime.now()


def format_date_spanish(date_obj: datetime) -> str:
    """
    Formatea una fecha al formato español "DD de MES de YYYY".

    Args:
        date_obj: Objeto datetime

    Returns:
        str: Fecha formateada en español
    """
    set_spanish_locale()
    return date_obj.strftime("%d de %B de %Y")
