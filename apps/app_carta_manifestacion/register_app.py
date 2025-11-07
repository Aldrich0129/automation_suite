#!/usr/bin/env python3
"""
Script para registrar la app en el backend.
============================================

Uso:
    python register_app.py

Requiere que el backend esté ejecutándose y que el usuario esté autenticado como admin.
"""

import sys
import os
from pathlib import Path

# Añadir el directorio core al path
CORE_PATH = Path(__file__).parent.parent.parent / "core"
sys.path.insert(0, str(CORE_PATH))

# Añadir el directorio del portal al path (para usar el cliente)
PORTAL_PATH = Path(__file__).parent.parent.parent / "portal" / "app"
sys.path.insert(0, str(PORTAL_PATH))

try:
    from client import BackendClient
except ImportError:
    print("Error: No se pudo importar BackendClient")
    print("Asegúrate de que el portal esté configurado correctamente.")
    sys.exit(1)


def register_app():
    """Registra la app en el backend."""
    app_data = {
        "id": "app_carta_manifestacion",
        "name": "Generador de Carta de Manifestación",
        "description": "Herramienta para generar cartas de manifestación de auditoría a partir de plantillas Word.",
        "path": "/app_carta_manifestacion",
        "tags": "Auditoría,Documentos",
        "enabled": True,
        "access_mode": "public"
    }

    client = BackendClient()

    try:
        print("Intentando crear la aplicación...")
        result = client.create_app(app_data)
        print(f"✅ Aplicación creada exitosamente: {result['name']}")
        print(f"   ID: {result['id']}")
        print(f"   Ruta: {result['path']}")
        print(f"   Estado: {'Activa' if result['enabled'] else 'Inactiva'}")

    except Exception as e:
        error_msg = str(e)
        if "Ya existe una aplicación" in error_msg:
            print("ℹ️  La aplicación ya existe. Intentando actualizar...")
            try:
                # Actualizar en lugar de crear
                update_data = {
                    "name": app_data["name"],
                    "description": app_data["description"],
                    "path": app_data["path"],
                    "tags": app_data["tags"],
                    "enabled": app_data["enabled"],
                    "access_mode": app_data["access_mode"]
                }
                result = client.update_app(app_data["id"], update_data)
                print(f"✅ Aplicación actualizada exitosamente: {result['name']}")
                print(f"   ID: {result['id']}")
                print(f"   Ruta: {result['path']}")
                print(f"   Estado: {'Activa' if result['enabled'] else 'Inactiva'}")
            except Exception as update_error:
                print(f"❌ Error al actualizar la aplicación: {update_error}")
                sys.exit(1)
        else:
            print(f"❌ Error al registrar la aplicación: {e}")
            print("\nAsegúrate de:")
            print("  1. El backend esté ejecutándose")
            print("  2. Estés autenticado como administrador")
            print("  3. La URL del backend sea correcta")
            sys.exit(1)


if __name__ == "__main__":
    print("=" * 50)
    print("Registro de App: Carta de Manifestación")
    print("=" * 50)
    print()

    register_app()

    print()
    print("=" * 50)
    print("Proceso completado")
    print("=" * 50)
