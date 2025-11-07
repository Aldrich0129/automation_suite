# 🏢 Automation Suite - Fase 2

Plataforma corporativa de automatización con portal web, backend administrativo y telemetría.

## 🌟 Características

### Fase 1 (Completada)
- ✅ Portal web con Streamlit
- ✅ Catálogo de aplicaciones con diseño moderno
- ✅ Soporte para subrutas
- ✅ Vista de 3 columnas con colores modernos

### Fase 2 (Actual)
- ✅ **Backend REST con FastAPI**
  - CRUD de aplicaciones
  - Control de acceso (público, password, SSO stub)
  - Ventanas temporales de disponibilidad
  - Gestión de programación

- ✅ **Panel de Administración**
  - Autenticación con sesiones
  - Gestión completa de aplicaciones
  - Configuración de contraseñas por app
  - Dashboard de métricas y telemetría

- ✅ **Telemetría**
  - Ingesta de eventos desde apps
  - Agregaciones y estadísticas
  - Gráficos de series temporales
  - Métricas por aplicación y tipo de evento

- ✅ **Base de Datos**
  - SQLite en desarrollo
  - PostgreSQL en producción
  - Migraciones con Alembic

## 📁 Estructura del Proyecto

```
automation-suite/
├── backend/                    # Backend FastAPI
│   ├── app/
│   │   ├── main.py            # Aplicación principal
│   │   ├── config.py          # Configuración
│   │   ├── db.py              # Base de datos
│   │   ├── models.py          # Modelos SQLAlchemy
│   │   ├── schemas.py         # Esquemas Pydantic
│   │   ├── routers/           # Endpoints
│   │   │   ├── apps.py        # CRUD aplicaciones
│   │   │   ├── auth.py        # Autenticación
│   │   │   ├── stats.py       # Estadísticas
│   │   │   ├── telemetry.py  # Ingesta de eventos
│   │   │   └── schedules.py  # Programación
│   │   ├── services/          # Lógica de negocio
│   │   │   ├── app_service.py
│   │   │   └── auth_service.py
│   │   ├── auth/              # Autenticación
│   │   │   ├── session.py
│   │   │   └── oidc_stub.py
│   │   └── utils/
│   │       └── cache.py       # Caché en memoria
│   ├── alembic/               # Migraciones
│   ├── tests/                 # Tests
│   ├── requirements.txt
│   └── run_local.sh
│
├── portal/                     # Portal Streamlit
│   ├── app/
│   │   ├── portal.py          # Catálogo principal
│   │   ├── admin_pages.py     # Panel admin
│   │   └── client.py          # Cliente HTTP
│   ├── apps_registry.yaml     # Seed de aplicaciones
│   ├── requirements.txt
│   └── run_local.sh
│
├── core/                       # Módulo común
│   └── core/
│       └── settings.py
│
├── .env.example                # Configuración de ejemplo
├── .gitignore
└── README.md
```

## 🚀 Instalación y Ejecución

### Requisitos Previos

- Python 3.9+
- pip

### 1. Configuración Inicial

```bash
# Clonar el repositorio
git clone <repository-url>
cd automation-suite

# Copiar archivo de configuración
cp .env.example .env

# Editar .env con tus configuraciones
nano .env
```

### 2. Iniciar el Backend

```bash
cd backend

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# o
.\venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar migraciones (opcional, se ejecutan automáticamente)
alembic upgrade head

# Iniciar servidor
./run_local.sh
# o manualmente:
# uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

El backend estará disponible en:
- **API:** http://localhost:8000
- **Documentación:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/healthz

### 3. Iniciar el Portal

```bash
cd portal

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Iniciar portal
./run_local.sh
# o manualmente:
# streamlit run app/portal.py --server.port=8501 --server.baseUrlPath=/portal
```

El portal estará disponible en:
- **Portal:** http://localhost:8501/portal
- **Admin:** http://localhost:8501/portal (pestaña "⚙️ Administración")

## 🔐 Credenciales por Defecto

Al iniciar por primera vez, se crea un usuario administrador:

- **Usuario:** `admin`
- **Contraseña:** `admin123`

> ⚠️ **Importante:** Cambia estas credenciales en producción editando el archivo `.env`

## 📖 Uso

### Portal Principal

1. Accede a http://localhost:8501/portal
2. Verás el catálogo de aplicaciones en formato de cuadrícula (3 columnas)
3. Las aplicaciones habilitadas aparecen con colores modernos
4. Las deshabilitadas están en la sección "En Desarrollo"

### Panel de Administración

El panel de administración está completamente integrado en el portal. Para acceder:

1. **Accede al Portal:** Abre http://localhost:8501/portal en tu navegador
2. **Ve a la pestaña "⚙️ Administración"** en la parte superior del portal
3. **Inicia sesión** con las credenciales de administrador:
   - Usuario: `admin`
   - Contraseña: `admin123`
4. **Gestiona aplicaciones** desde la pestaña "📦 Aplicaciones":
   - **Crear apps:** Click en "➕ Nueva Aplicación" y completa el formulario
   - **Editar apps:** Expande cualquier aplicación para ver opciones
   - **Activar/Desactivar:** Toggle rápido para habilitar/deshabilitar aplicaciones
   - **Configurar contraseñas:** Botón "🔑 Contraseña" para apps con `access_mode=password`
   - **Programar disponibilidad:** Botón "📅 Horario" para establecer ventanas temporales (`enabled_from` / `enabled_until`)
   - **Eliminar apps:** Botón "🗑️ Eliminar" con confirmación
5. **Consulta métricas** desde la pestaña "📊 Métricas":
   - **Resumen global:** Totales de eventos por aplicación (últimos 7-90 días)
   - **Gráficos de barras:** Comparación visual entre aplicaciones
   - **Series temporales:** Evolución diaria de eventos por tipo (open, generate_document, error, custom)
   - **Filtros:** Selecciona aplicación, tipo de evento y período

#### Flujo completo de administración

```bash
# 1. Asegúrate de que el backend esté ejecutándose
cd backend
./run_local.sh  # O: uvicorn app.main:app --reload

# 2. En otra terminal, inicia el portal
cd portal
./run_local.sh  # O: streamlit run app/portal.py --server.port=8501 --server.baseUrlPath=/portal

# 3. Accede al portal
# Navega a: http://localhost:8501/portal

# 4. Ve a la pestaña "⚙️ Administración" y haz login

# 5. Crea una aplicación de prueba
# - ID: app_test
# - Nombre: Aplicación de Prueba
# - Path: /apps/test
# - Modo de acceso: public
# - Habilitada: Sí

# 6. La aplicación aparecerá automáticamente en el catálogo principal

# 7. (Opcional) Cambia el modo de acceso a "password" y establece una contraseña
# Al hacer click en "Abrir" desde el catálogo, pedirá la contraseña

# 8. (Opcional) Envía telemetría de prueba
curl -X POST http://localhost:8000/api/telemetry \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "app_test",
    "event_type": "open",
    "user_id": "test_user"
  }'

# 9. Consulta las métricas en la pestaña "📊 Métricas"
```

### Modos de Acceso

Las aplicaciones pueden tener 3 modos de acceso:

- **public:** Acceso libre sin autenticación
- **password:** Requiere contraseña (configurable por app)
- **sso:** SSO futuro (stub por ahora)

### Telemetría

Las aplicaciones pueden reportar eventos al backend:

```bash
curl -X POST http://localhost:8000/api/telemetry \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "app_01",
    "event_type": "generate_document",
    "user_id": "usuario123",
    "meta": {"documento": "reporte.pdf"}
  }'
```

Tipos de evento soportados:
- `open`: Apertura de la app
- `generate_document`: Generación de documento
- `error`: Error en la app
- `custom`: Evento personalizado

## 🧪 Tests

```bash
cd backend
pytest tests/
```

## 🗄️ Base de Datos

### SQLite (Desarrollo)

Por defecto, usa SQLite en archivo `automation.db`.

### PostgreSQL (Producción)

1. Instala PostgreSQL
2. Crea una base de datos:
   ```sql
   CREATE DATABASE automation_suite;
   ```
3. Actualiza `.env`:
   ```
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/automation_suite
   ```

### Migraciones

```bash
# Crear nueva migración
alembic revision --autogenerate -m "Descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Revertir última migración
alembic downgrade -1
```

## 🔧 Troubleshooting

### El portal no muestra aplicaciones

**Síntoma:** Al abrir el portal, aparece el mensaje "No se encontraron aplicaciones registradas"

**Soluciones:**

1. **Verifica que el backend esté ejecutándose:**
   ```bash
   curl http://localhost:8000/api/healthz
   # Debe responder: {"status": "healthy"}
   ```

2. **Revisa la configuración del backend en `.env`:**
   ```bash
   BACKEND_BASE_URL=http://localhost:8000
   ```

3. **Crea aplicaciones desde el panel de administración:**
   - Ve a "⚙️ Administración" → "📦 Aplicaciones" → "➕ Nueva Aplicación"

4. **Verifica que existan apps en el backend:**
   ```bash
   # Debes tener sesión admin, o usa curl con cookies
   curl http://localhost:8000/api/apps
   ```

### Error "No se pudo conectar al backend"

**Síntoma:** Aparece un error al cargar el catálogo o al hacer login

**Soluciones:**

1. **Verifica que el backend esté corriendo en el puerto 8000:**
   ```bash
   lsof -i :8000
   # O en Windows: netstat -ano | findstr :8000
   ```

2. **Revisa la variable `BACKEND_BASE_URL` en `.env`:**
   - Debe apuntar a `http://localhost:8000`
   - Si cambias el puerto del backend, actualiza esta variable

3. **Verifica CORS en el backend:**
   - En `.env`, asegúrate de que `CORS_ALLOW_ORIGIN=http://localhost:8501`
   - Si cambias el puerto del portal, actualiza esta variable

### Error 401/403 en el panel de administración

**Síntoma:** No puedes hacer login o las operaciones de admin fallan con "No autenticado"

**Soluciones:**

1. **Verifica las credenciales:**
   - Usuario: `admin`
   - Contraseña: `admin123`
   - Puedes cambiarlas en `.env` con `ADMIN_DEFAULT_USER` y `ADMIN_DEFAULT_PASS`

2. **Revisa las cookies del navegador:**
   - El backend usa cookies HttpOnly (`admin_session`)
   - Si usas incógnito o borras cookies, debes volver a hacer login

3. **Verifica que la sesión no haya expirado:**
   - Las sesiones duran 8 horas por defecto (`SESSION_EXPIRE_HOURS=8`)

### La aplicación con contraseña no valida correctamente

**Síntoma:** Ingresas la contraseña en el catálogo pero sigue diciendo "Contraseña incorrecta"

**Soluciones:**

1. **Verifica que la contraseña esté configurada en el backend:**
   - Ve a "⚙️ Administración" → Expande la app → "🔑 Contraseña"
   - Ingresa la contraseña nuevamente

2. **Revisa que el `access_mode` sea "password":**
   - Si es "public", no pedirá contraseña
   - Si es "sso", está deshabilitado por ahora

### Las métricas no muestran datos

**Síntoma:** En "📊 Métricas" aparece "No hay eventos registrados"

**Soluciones:**

1. **Envía eventos de telemetría de prueba:**
   ```bash
   curl -X POST http://localhost:8000/api/telemetry \
     -H "Content-Type: application/json" \
     -d '{
       "app_id": "tu_app_id",
       "event_type": "open",
       "user_id": "test"
     }'
   ```

2. **Verifica el período seleccionado:**
   - Las métricas solo muestran eventos de los últimos N días (7, 15, 30, etc.)
   - Si los eventos son antiguos, aumenta el período

3. **Revisa que el `app_id` en telemetría coincida con el ID de la app:**
   - Debe ser exactamente el mismo que el ID registrado

### El portal no carga con `--server.baseUrlPath=/portal`

**Síntoma:** Al ejecutar `streamlit run app/portal.py --server.baseUrlPath=/portal` el portal no carga o da error 404

**Soluciones:**

1. **Accede a la URL correcta:**
   - **Correcto:** http://localhost:8501/portal
   - **Incorrecto:** http://localhost:8501 (sin /portal)

2. **Verifica que el script `run_local.sh` tenga el parámetro:**
   ```bash
   streamlit run app/portal.py --server.port=8501 --server.baseUrlPath=/portal
   ```

3. **Si usas un proxy/nginx, configura el `baseUrlPath` correctamente**

## 🔧 Configuración Avanzada

### Variables de Entorno

Ver `.env.example` para todas las opciones disponibles.

Principales configuraciones:

```bash
# Backend
DATABASE_URL=sqlite+aiosqlite:///./automation.db
SECRET_KEY=tu_clave_secreta
ADMIN_DEFAULT_USER=admin
ADMIN_DEFAULT_PASS=admin123
CORS_ALLOW_ORIGIN=http://localhost:8501

# Portal
BACKEND_BASE_URL=http://localhost:8000
PORTAL_BASE_PATH=/portal
```

### Rate Limiting

Configurable por IP en el backend:

```bash
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100  # Requests por ventana
RATE_LIMIT_WINDOW=60     # Segundos
```

### Cache

El catálogo público se cachea con TTL configurable:

```bash
CATALOG_CACHE_TTL=15  # Segundos
```

### Telemetría Protegida

Opcionalmente, protege el endpoint de telemetría con un token:

```bash
TELEMETRY_TOKEN=mi_token_secreto
```

Luego envía el token en el header:
```bash
curl -X POST http://localhost:8000/api/telemetry \
  -H "X-Telemetry-Token: mi_token_secreto" \
  -H "Content-Type: application/json" \
  -d '...'
```

## 🐳 Despliegue con Docker

> TODO: Añadir Dockerfile y docker-compose.yml

## 🔒 Seguridad

- ✅ Contraseñas hasheadas con bcrypt
- ✅ Sesiones firmadas con HMAC
- ✅ CORS configurables
- ✅ Rate limiting por IP
- ✅ Cookies HttpOnly
- ✅ Validación con Pydantic

## 🛣️ Roadmap

### Próximas Funcionalidades
- [ ] SSO con OIDC (Keycloak, Auth0, etc.)
- [ ] Roles y permisos granulares
- [ ] Logs estructurados con ELK
- [ ] Containerización (Docker)
- [ ] CI/CD con GitHub Actions
- [ ] Notificaciones (email, Slack)
- [ ] API keys para telemetría
- [ ] Dashboard en tiempo real

## 📝 Licencia

[Tu licencia aquí]

## 👥 Contribuciones

[Instrucciones de contribución]

## 📞 Soporte

[Información de contacto o issues]

---

Desarrollado con ❤️ para automatizaciones corporativas
