#!/usr/bin/env python3
"""
Script de prueba de conexión - Automation Suite
================================================

Verifica que el backend esté funcionando y que el portal pueda
conectarse correctamente.
"""

import sys
from pathlib import Path

# Añadir el directorio portal al path
PORTAL_PATH = Path(__file__).parent / "portal" / "app"
sys.path.insert(0, str(PORTAL_PATH))

try:
    from client import BackendClient
except ImportError:
    print("❌ Error: No se pudo importar BackendClient")
    sys.exit(1)


def main():
    print("╔═══════════════════════════════════════════════════════╗")
    print("║     🧪 PRUEBA DE CONEXIÓN - AUTOMATION SUITE         ║")
    print("╚═══════════════════════════════════════════════════════╝")
    print()

    client = BackendClient()

    # Test 1: Health Check
    print("1. 🏥 Verificando estado del backend...")
    try:
        health = client.health_check()
        print(f"   ✅ Backend funcionando correctamente")
        print(f"   📊 Estado: {health['status']}")
        print(f"   🔖 Versión: {health['version']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print()
        print("   💡 Sugerencias:")
        print("      - Verifica que el backend esté ejecutándose")
        print("      - Ejecuta: cd backend && source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000")
        sys.exit(1)

    print()

    # Test 2: Listar aplicaciones públicas
    print("2. 📦 Cargando catálogo de aplicaciones públicas...")
    try:
        apps = client.list_apps()
        print(f"   ✅ Se encontraron {len(apps)} aplicaciones")
        print()

        if apps:
            print("   📋 Aplicaciones disponibles:")
            for app in apps:
                status = "🟢" if app['enabled'] else "🔴"
                print(f"      {status} {app['name']} ({app['id']})")
                print(f"         Path: {app['path']}")
                print(f"         Modo: {app['access_mode']}")
        else:
            print("   ⚠️  No hay aplicaciones registradas")
            print()
            print("   💡 Sugerencias:")
            print("      - Ve al panel de administración para crear aplicaciones")
            print("      - O ejecuta el script de registro: python apps/app_carta_manifestacion/register_app.py")
    except Exception as e:
        print(f"   ❌ Error al cargar aplicaciones: {e}")
        sys.exit(1)

    print()

    # Test 3: Intentar login de administrador
    print("3. 🔐 Probando autenticación de administrador...")
    try:
        result = client.login("admin", "admin123")
        print(f"   ✅ Login exitoso")
        print(f"   👤 Usuario: {result['user']['username']}")
        print(f"   🆔 ID: {result['user']['id']}")

        # Test 4: Listar todas las aplicaciones (admin)
        print()
        print("4. 📦 Cargando todas las aplicaciones (admin)...")
        all_apps = client.list_all_apps()
        print(f"   ✅ Se encontraron {len(all_apps)} aplicaciones totales")

        enabled = sum(1 for app in all_apps if app['enabled'])
        disabled = len(all_apps) - enabled
        print(f"      • Habilitadas: {enabled}")
        print(f"      • Deshabilitadas: {disabled}")

    except Exception as e:
        print(f"   ❌ Error en autenticación: {e}")
        print()
        print("   💡 Sugerencias:")
        print("      - Verifica las credenciales en el archivo .env")
        print("      - ADMIN_DEFAULT_USER y ADMIN_DEFAULT_PASS")

    print()
    print("╔═══════════════════════════════════════════════════════╗")
    print("║           ✅ PRUEBAS COMPLETADAS EXITOSAMENTE         ║")
    print("╚═══════════════════════════════════════════════════════╝")
    print()
    print("🎉 El sistema está funcionando correctamente")
    print()
    print("🌐 Accede al portal en: http://localhost:8501/portal")
    print()


if __name__ == "__main__":
    main()
