"""
Aplicación Principal - Automation Suite Backend
================================================

FastAPI backend para gestión de aplicaciones, telemetría y métricas.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy import select
import yaml

from app.config import settings
from app.db import init_db, get_db
from app.models import App
from app.services.auth_service import ensure_default_admin
from app.routers import apps, stats, telemetry, schedules, auth
from app.schemas import HealthResponse

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
)
logger = logging.getLogger(__name__)


# ===========================
# Lifecycle
# ===========================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestor de ciclo de vida de la aplicación.

    Ejecuta tareas de inicialización al arrancar y limpieza al cerrar.
    """
    logger.info("Inicializando backend...")

    # Inicializar base de datos
    await init_db()
    logger.info("Base de datos inicializada")

    # Crear admin por defecto
    async for db in get_db():
        await ensure_default_admin(db)
        logger.info(f"Usuario admin por defecto verificado: {settings.ADMIN_DEFAULT_USER}")

        # Importar apps desde YAML si existe y la tabla está vacía
        await seed_apps_from_yaml(db)

        break

    logger.info("Backend listo ✓")

    yield

    # Limpieza al cerrar
    logger.info("Cerrando backend...")


async def seed_apps_from_yaml(db):
    """
    Importa aplicaciones desde apps_registry.yaml si existe.

    Solo importa si la tabla de apps está vacía.
    """
    # Verificar si hay apps
    stmt = select(App)
    result = await db.execute(stmt)
    existing_apps = result.scalars().all()

    if existing_apps:
        logger.info("Ya existen aplicaciones en la BD, omitiendo seed")
        return

    # Buscar archivo YAML
    yaml_path = None

    if settings.APPS_REGISTRY_PATH:
        yaml_path = Path(settings.APPS_REGISTRY_PATH)
    else:
        # Buscar en ruta por defecto
        default_path = Path(__file__).parent.parent.parent / "portal" / "apps_registry.yaml"
        if default_path.exists():
            yaml_path = default_path

    if not yaml_path or not yaml_path.exists():
        logger.info("No se encontró apps_registry.yaml para seed")
        return

    # Cargar y seed
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            apps_data = data.get('apps', [])

        for app_data in apps_data:
            app = App(
                id=app_data.get('id'),
                name=app_data.get('name'),
                description=app_data.get('description'),
                path=app_data.get('path'),
                tags=','.join(app_data.get('tags', [])),
                enabled=app_data.get('enabled', True),
                access_mode='public',
            )
            db.add(app)

        await db.commit()
        logger.info(f"Seed completado: {len(apps_data)} aplicaciones importadas desde YAML")
    except Exception as e:
        logger.error(f"Error al importar apps desde YAML: {e}")


# ===========================
# Aplicación FastAPI
# ===========================

app = FastAPI(
    title="Automation Suite API",
    description="API REST para gestión de aplicaciones, telemetría y métricas",
    version="2.0.0",
    lifespan=lifespan
)


# ===========================
# Middlewares
# ===========================

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CORS_ALLOW_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Rate limiting simple (por IP)
from collections import defaultdict
from time import time

rate_limit_store = defaultdict(list)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """
    Middleware de rate limiting simple por IP.

    Aplica límite solo a rutas /admin/* y /telemetry.
    """
    if not settings.RATE_LIMIT_ENABLED:
        return await call_next(request)

    path = request.url.path

    # Solo aplicar a ciertas rutas
    if not (path.startswith("/api/admin") or path.startswith("/api/telemetry")):
        return await call_next(request)

    client_ip = request.client.host
    now = time()

    # Limpiar requests antiguos
    rate_limit_store[client_ip] = [
        req_time for req_time in rate_limit_store[client_ip]
        if now - req_time < settings.RATE_LIMIT_WINDOW
    ]

    # Verificar límite
    if len(rate_limit_store[client_ip]) >= settings.RATE_LIMIT_REQUESTS:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Demasiadas solicitudes. Intenta más tarde."}
        )

    # Registrar request
    rate_limit_store[client_ip].append(now)

    return await call_next(request)


# Logging de requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware para logging de requests."""
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"{request.method} {request.url.path} -> {response.status_code}")
    return response


# ===========================
# Manejadores de Errores
# ===========================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Manejador de errores de validación."""
    logger.warning(f"Error de validación: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Manejador global de excepciones."""
    logger.error(f"Error no manejado: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Error interno del servidor"}
    )


# ===========================
# Routers
# ===========================

# Health check
@app.get("/api/healthz", response_model=HealthResponse, tags=["health"])
async def health_check():
    """
    Health check del backend.

    Returns:
        Estado del servicio
    """
    return HealthResponse()


# Routers de aplicación
app.include_router(apps.router, prefix="/api")
app.include_router(stats.router, prefix="/api")
app.include_router(telemetry.router, prefix="/api")
app.include_router(schedules.router, prefix="/api")
app.include_router(auth.router, prefix="/api")


# ===========================
# Punto de Entrada
# ===========================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level="info"
    )
