# 🔌 Arquitectura de Puertos - Automation Suite

## Resumen

Este documento describe la arquitectura de puertos del sistema Automation Suite, diseñada para facilitar la escalabilidad y evitar conflictos entre servicios.

## Esquema de Puertos

### Servicios Principales

| Servicio | Puerto | URL | Descripción |
|----------|--------|-----|-------------|
| **Portal Web** | `8600` | http://localhost:8600/portal | Portal web principal, catálogo de apps y panel de administración |
| **Backend API** | `8601` | http://localhost:8601 | API REST, documentación Swagger (/docs), health check |

### Aplicaciones Modulares

| Aplicación | Puerto | URL | Descripción |
|------------|--------|-----|-------------|
| **Generador de Cartas de Manifestación** | `8602` | http://localhost:8602/app_carta_manifestacion | App Streamlit para generación de cartas |
| **Aplicación 2** | `8603` | http://localhost:8603/* | (Reservado para futuras apps) |
| **Aplicación 3** | `8604` | http://localhost:8604/* | (Reservado para futuras apps) |
| **Aplicación N** | `860N` | http://localhost:860N/* | Esquema secuencial escalable |

## Ventajas de esta Arquitectura

### 1. Escalabilidad
- Cada nueva aplicación obtiene automáticamente el siguiente puerto disponible
- No hay límite práctico de aplicaciones (8602-8699 = 98 aplicaciones posibles)
- Fácil de recordar: 86XX para todo el ecosistema

### 2. Claridad y Consistencia
- Los servicios principales tienen puertos fijos y bien conocidos
- El patrón secuencial facilita la documentación
- Evita confusión sobre qué servicio corre en qué puerto

### 3. Aislamiento
- Cada aplicación puede ejecutarse independientemente
- Facilita debugging al aislar servicios específicos
- Permite desarrollo paralelo de múltiples aplicaciones

### 4. Sin Conflictos
- El esquema numérico evita colisiones de puertos
- Fácil identificar puertos disponibles
- Compatible con firewalls y proxies

## Configuración

### Archivo `.env`

```bash
# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8601
BACKEND_BASE_URL=http://localhost:8601

# Portal
CORS_ALLOW_ORIGIN=http://localhost:8600
PORTAL_BASE_PATH=/portal
```

### Scripts de Inicio

**Backend (`backend/run_local.sh`):**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8601 --reload
```

**Portal (`portal/run_local.sh`):**
```bash
streamlit run app/portal.py --server.port=8600 --server.baseUrlPath=/portal
```

**Aplicación (`apps/app_*/run_local.sh`):**
```bash
APP_PORT=8602  # Incrementar para cada nueva app
streamlit run app/ui.py --server.port=$APP_PORT --server.baseUrlPath=/app_name
```

## Guía para Crear Nueva Aplicación

Cuando crees una nueva aplicación, sigue estos pasos:

### 1. Determinar el Puerto
```bash
# Listar puertos en uso
lsof -i :8602
lsof -i :8603
# etc.

# Asigna el siguiente puerto disponible
NEXT_PORT=8603  # Por ejemplo
```

### 2. Configurar el Script de Inicio

**`apps/mi_nueva_app/run_local.sh`:**
```bash
#!/bin/bash
APP_PORT=8603  # Puerto asignado
BASE_URL_PATH="/mi_nueva_app"
BACKEND_URL=${BACKEND_BASE_URL:-"http://localhost:8601"}

echo "Puerto: $APP_PORT"
echo "Ruta base: $BASE_URL_PATH"
echo "Backend URL: $BACKEND_URL"

export BACKEND_BASE_URL=$BACKEND_URL

streamlit run app/ui.py \
  --server.port=$APP_PORT \
  --server.baseUrlPath=$BASE_URL_PATH
```

### 3. Configurar Streamlit (si aplica)

**`apps/mi_nueva_app/.streamlit/config.toml`:**
```toml
[server]
port = 8603
headless = true
enableCORS = false
enableXsrfProtection = false
```

### 4. Documentar en el README

**`apps/mi_nueva_app/README.md`:**
```markdown
## Ejecución Local

La aplicación estará disponible en: http://localhost:8603/mi_nueva_app

### Comando directo
streamlit run app/ui.py \
  --server.port=8603 \
  --server.baseUrlPath=/mi_nueva_app
```

### 5. Registrar en el Backend

El puerto se usa solo para desarrollo local. Para integración con el portal:

```python
# apps/mi_nueva_app/register_app.py
app_data = {
    "id": "mi_nueva_app",
    "name": "Mi Nueva Aplicación",
    "path": "/mi_nueva_app",  # Path usado en el portal
    "description": "Descripción de la app",
    "tags": "tag1,tag2",
    "enabled": True,
    "access_mode": "public"
}
```

## Comandos Útiles

### Verificar Puertos en Uso
```bash
# Linux/Mac
lsof -i :8600  # Portal
lsof -i :8601  # Backend
lsof -i :8602  # App 1
lsof -i :8603  # App 2

# Listar todos los puertos 86XX
lsof -i :860  # Muestra todos

# Windows
netstat -ano | findstr :8600
netstat -ano | findstr :8601
```

### Ver Todos los Servicios del Sistema
```bash
ps aux | grep -E "uvicorn|streamlit"
```

### Liberar un Puerto Específico
```bash
# Encontrar el PID
lsof -ti :8603

# Matar el proceso
kill $(lsof -ti :8603)
```

## Migración desde Esquema Anterior

### Cambios Realizados

| Servicio | Puerto Anterior | Puerto Nuevo | Cambio |
|----------|----------------|--------------|--------|
| Portal | 8501 | 8600 | -101 |
| Backend | 8000 | 8601 | +601 |
| App Carta Manifestación | 8601 | 8602 | +1 |

### Archivos Actualizados

1. `.env.example` - Variables de entorno
2. `start_system.sh` - Script de inicio del sistema
3. `backend/run_local.sh` - Script de backend
4. `portal/run_local.sh` - Script de portal
5. `apps/app_carta_manifestacion/run_local.sh` - Script de app
6. `apps/app_carta_manifestacion/.streamlit/config.toml` - Config Streamlit
7. `test_connection.py` - Script de pruebas
8. `README.md` - Documentación principal
9. `ACCESO_ADMIN.md` - Guía de administración
10. `apps/app_carta_manifestacion/README.md` - Docs de app

### Pasos de Migración

Si estás migrando desde el esquema anterior:

1. **Actualiza tu archivo `.env`:**
   ```bash
   cp .env.example .env
   # Edita las variables según tu configuración
   ```

2. **Detén servicios en puertos antiguos:**
   ```bash
   pkill -f "uvicorn.*8000"
   pkill -f "streamlit.*8501"
   pkill -f "streamlit.*8601"
   ```

3. **Inicia con nuevos puertos:**
   ```bash
   ./start_system.sh
   ```

4. **Actualiza bookmarks/favoritos del navegador:**
   - Portal: http://localhost:8600/portal
   - Backend: http://localhost:8601

## Troubleshooting

### Puerto ya en uso

**Error:** `Address already in use`

**Solución:**
```bash
# Encuentra qué está usando el puerto
lsof -i :8600

# Mata el proceso
kill -9 <PID>

# O usa el script de inicio que lo maneja automáticamente
./start_system.sh
```

### CORS errors

**Error:** `Access to fetch blocked by CORS policy`

**Solución:**
Verifica que `CORS_ALLOW_ORIGIN` en `.env` coincida con el puerto del portal:
```bash
CORS_ALLOW_ORIGIN=http://localhost:8600
```

### Backend no responde

**Síntoma:** Portal no puede conectar al backend

**Solución:**
```bash
# Verifica que el backend esté en el puerto correcto
curl http://localhost:8601/api/healthz

# Debe responder: {"status":"ok","version":"2.0.0"}
```

## Referencias

- **README principal:** [README.md](README.md)
- **Guía de administración:** [ACCESO_ADMIN.md](ACCESO_ADMIN.md)
- **Ejemplo de app:** [apps/app_carta_manifestacion/README.md](apps/app_carta_manifestacion/README.md)

---

**Última actualización:** 2025-11-07
**Versión del esquema:** 2.0
