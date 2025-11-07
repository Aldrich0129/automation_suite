#!/usr/bin/env python3
"""
CLI de Administración - Automation Suite Backend
=================================================

Script de utilidad para gestionar aplicaciones desde la línea de comandos.
"""

import sys
import os
from pathlib import Path
import json
import argparse

# Añadir el directorio portal al path para usar el cliente
PORTAL_PATH = Path(__file__).parent.parent / "portal" / "app"
sys.path.insert(0, str(PORTAL_PATH))

try:
    from client import BackendClient
except ImportError:
    print("Error: No se pudo importar BackendClient")
    sys.exit(1)


def login(username: str, password: str):
    """Inicia sesión como administrador."""
    client = BackendClient()
    try:
        result = client.login(username, password)
        print(f"✅ Sesión iniciada como: {username}")
        return client
    except Exception as e:
        print(f"❌ Error al iniciar sesión: {e}")
        sys.exit(1)


def list_apps(client: BackendClient, show_all: bool = False):
    """Lista todas las aplicaciones."""
    try:
        if show_all:
            apps = client.list_all_apps()
        else:
            apps = client.list_apps()

        print(f"\n📦 Aplicaciones registradas ({len(apps)}):\n")

        for app in apps:
            status = "🟢" if app['enabled'] else "🔴"
            print(f"{status} {app['name']} ({app['id']})")
            print(f"   Path: {app['path']}")
            print(f"   Modo: {app['access_mode']}")
            print(f"   Tags: {app.get('tags', 'N/A')}")
            print()

    except Exception as e:
        print(f"❌ Error al listar aplicaciones: {e}")


def register_app(client: BackendClient, app_data: dict):
    """Registra una nueva aplicación."""
    try:
        result = client.create_app(app_data)
        print(f"✅ Aplicación '{result['name']}' registrada exitosamente")
        print(f"   ID: {result['id']}")
        print(f"   Path: {result['path']}")
        return result
    except Exception as e:
        error_msg = str(e)
        if "Ya existe" in error_msg:
            print(f"ℹ️  La aplicación ya existe. Actualizando...")
            try:
                result = client.update_app(app_data["id"], app_data)
                print(f"✅ Aplicación '{result['name']}' actualizada exitosamente")
                return result
            except Exception as update_error:
                print(f"❌ Error al actualizar: {update_error}")
        else:
            print(f"❌ Error al registrar aplicación: {e}")


def main():
    parser = argparse.ArgumentParser(description="CLI de Administración - Automation Suite")
    parser.add_argument("action", choices=["list", "register"], help="Acción a realizar")
    parser.add_argument("--username", "-u", default="admin", help="Usuario administrador")
    parser.add_argument("--password", "-p", default="admin123", help="Contraseña")
    parser.add_argument("--all", "-a", action="store_true", help="Mostrar todas las apps (incluye deshabilitadas)")
    parser.add_argument("--app-data", "-d", help="JSON con datos de la aplicación (para register)")

    args = parser.parse_args()

    # Login
    print("🔐 Iniciando sesión...")
    client = login(args.username, args.password)

    # Ejecutar acción
    if args.action == "list":
        list_apps(client, args.all)

    elif args.action == "register":
        if not args.app_data:
            print("❌ Error: --app-data es requerido para 'register'")
            sys.exit(1)

        try:
            app_data = json.loads(args.app_data)
            register_app(client, app_data)
        except json.JSONDecodeError:
            print("❌ Error: --app-data debe ser un JSON válido")
            sys.exit(1)


if __name__ == "__main__":
    main()
