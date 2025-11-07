"""
Sistema de Caché - Automation Suite Backend
============================================

Implementa un sistema de caché en memoria con TTL (Time To Live).
"""

import time
from typing import Any, Dict, Optional
from threading import Lock


class CacheEntry:
    """Entrada de caché con timestamp."""

    def __init__(self, value: Any, ttl: int):
        self.value = value
        self.expires_at = time.time() + ttl

    def is_expired(self) -> bool:
        """Verifica si la entrada ha expirado."""
        return time.time() > self.expires_at


class TTLCache:
    """
    Caché simple con Time To Live.

    Implementa un diccionario en memoria con expiración automática.
    """

    def __init__(self):
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()

    def get(self, key: str) -> Optional[Any]:
        """
        Obtiene un valor del caché.

        Args:
            key: Clave del valor a obtener

        Returns:
            El valor almacenado o None si no existe o expiró
        """
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None

            if entry.is_expired():
                del self._cache[key]
                return None

            return entry.value

    def set(self, key: str, value: Any, ttl: int):
        """
        Almacena un valor en el caché con TTL.

        Args:
            key: Clave del valor
            value: Valor a almacenar
            ttl: Time To Live en segundos
        """
        with self._lock:
            self._cache[key] = CacheEntry(value, ttl)

    def delete(self, key: str):
        """
        Elimina un valor del caché.

        Args:
            key: Clave del valor a eliminar
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]

    def clear(self):
        """Limpia todo el caché."""
        with self._lock:
            self._cache.clear()

    def cleanup_expired(self):
        """Elimina todas las entradas expiradas."""
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            for key in expired_keys:
                del self._cache[key]


# Instancia global del caché
cache = TTLCache()
