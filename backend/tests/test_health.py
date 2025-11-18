"""
Tests de Health Check - Automation Suite Backend
=================================================

Tests básicos de disponibilidad del servicio.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    """Test del endpoint de health check."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/healthz")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "2.0.0"
    assert "timestamp" in data
