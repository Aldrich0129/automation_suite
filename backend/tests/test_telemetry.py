"""
Tests de Telemetría - Automation Suite Backend
===============================================

Tests de ingesta de eventos.
"""

import pytest
from httpx import AsyncClient
from app.models import App


@pytest.mark.asyncio
async def test_ingest_telemetry_without_app(client: AsyncClient):
    """Test de telemetría con app inexistente."""
    event_data = {
        "app_id": "nonexistent_app",
        "event_type": "open",
        "user_id": "test_user",
        "meta": {"test": "data"}
    }

    response = await client.post("/api/telemetry", json=event_data)

    # Debe fallar porque la app no existe
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_ingest_telemetry_with_app(client: AsyncClient, db_session):
    """Test de telemetría con app existente."""
    # Crear app primero
    app = App(
        id="test_app",
        name="Test App",
        path="/test",
        enabled=True
    )
    db_session.add(app)
    await db_session.commit()

    # Enviar telemetría
    event_data = {
        "app_id": "test_app",
        "event_type": "open",
        "user_id": "test_user",
        "meta": {"test": "data"}
    }

    response = await client.post("/api/telemetry", json=event_data)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "event_id" in data
