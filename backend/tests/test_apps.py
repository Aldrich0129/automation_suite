"""
Tests de Aplicaciones - Automation Suite Backend
=================================================

Tests de CRUD de aplicaciones.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_app(client: AsyncClient):
    """Test de creación de aplicación (requiere auth, se espera 401)."""
    app_data = {
        "id": "test_app",
        "name": "Test App",
        "description": "Test description",
        "path": "/test",
        "enabled": True,
        "access_mode": "public"
    }

    response = await client.post("/api/admin/apps", json=app_data)

    # Sin autenticación, debe fallar
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_public_apps(client: AsyncClient):
    """Test de listado de apps públicas."""
    response = await client.get("/api/apps")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
