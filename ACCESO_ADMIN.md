# 🔐 Guía de Acceso al Panel de Administración

## Inicio Rápido

### Opción 1: Usar el script de inicio automático (Recomendado)

```bash
cd /home/user/automation_suite
./start_system.sh
```

Este script:
- ✅ Verifica y crea el archivo `.env` si no existe
- ✅ Inicia el backend automáticamente
- ✅ Inicia el portal automáticamente
- ✅ Muestra las URLs y credenciales de acceso
- ✅ Gestiona los servicios de forma inteligente

### Opción 2: Inicio manual

#### 1. Iniciar el Backend

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8601
```

#### 2. Iniciar el Portal (en otra terminal)

```bash
cd portal
source venv/bin/activate
streamlit run app/portal.py --server.port=8600 --server.baseUrlPath=/portal
```

## 🔑 Credenciales de Administrador

**Estas son las credenciales por defecto configuradas en el archivo `.env`:**

- **Usuario:** `admin`
- **Contraseña:** `admin123`

> ⚠️ **IMPORTANTE:** Estas credenciales están definidas en el archivo `.env`:
> - `ADMIN_DEFAULT_USER=admin`
> - `ADMIN_DEFAULT_PASS=admin123`
>
> Para cambiarlas, edita el archivo `.env` y reinicia el backend.

## 🌐 URLs de Acceso

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Portal Principal** | http://localhost:8600/portal | Catálogo de aplicaciones |
| **Panel de Admin** | http://localhost:8600/portal → Pestaña "⚙️ Administración" | Gestión de aplicaciones y métricas |
| **Backend API** | http://localhost:8601 | API REST del backend |
| **Documentación API** | http://localhost:8601/docs | Documentación interactiva (Swagger) |
| **Health Check** | http://localhost:8601/api/healthz | Verificación de estado |

## 📋 Pasos para Acceder al Panel de Administración

1. **Abre el portal en tu navegador:**
   ```
   http://localhost:8600/portal
   ```

2. **Ve a la pestaña "⚙️ Administración"** en la parte superior

3. **Inicia sesión** con las credenciales:
   - Usuario: `admin`
   - Contraseña: `admin123`

4. **¡Listo!** Ahora puedes:
   - ✅ Crear nuevas aplicaciones
   - ✅ Editar aplicaciones existentes
   - ✅ Activar/Desactivar aplicaciones
   - ✅ Configurar contraseñas de acceso
   - ✅ Programar horarios de disponibilidad
   - ✅ Ver métricas y estadísticas de uso

## 📦 Gestión de Aplicaciones

### Crear una Nueva Aplicación

1. Ve a **Administración → 📦 Aplicaciones**
2. Click en **"➕ Nueva Aplicación"**
3. Completa el formulario:
   - **ID:** Identificador único (ej: `app_ejemplo`)
   - **Nombre:** Nombre descriptivo
   - **Path:** Ruta de la aplicación (ej: `/apps/ejemplo`)
   - **Descripción:** Breve descripción
   - **Tags:** Etiquetas separadas por comas
   - **Modo de acceso:** `public`, `password` o `sso`
   - **Habilitada:** Marcar si quieres que esté activa

4. Click en **"✅ Crear"**

### Editar una Aplicación

1. Ve a **Administración → 📦 Aplicaciones**
2. Expande la aplicación que deseas editar
3. Usa los botones de acción:
   - **✅ Activar / ⏸ Desactivar:** Cambiar estado
   - **🔑 Contraseña:** Configurar/cambiar contraseña
   - **📅 Horario:** Programar disponibilidad
   - **🗑️ Eliminar:** Eliminar aplicación

### Configurar Contraseña de Acceso

1. Expande la aplicación
2. Click en **"🔑 Contraseña"**
3. Ingresa la nueva contraseña
4. Click en **"💾 Guardar"**

**Nota:** Esto automáticamente cambiará el `access_mode` a `password`.

## 📊 Ver Métricas y Estadísticas

1. Ve a **Administración → 📊 Métricas**
2. Selecciona el período (7, 15, 30, 60 o 90 días)
3. Revisa:
   - **Resumen global** de eventos
   - **Gráficos de barras** por aplicación
   - **Series temporales** de eventos por tipo

## 🔧 Troubleshooting

### No puedo acceder al panel de administración

**Problema:** El botón de login no funciona o muestra error

**Solución:**
1. Verifica que el backend esté ejecutándose:
   ```bash
   curl http://localhost:8601/api/healthz
   ```
   Debe responder: `{"status": "ok", ...}`

2. Verifica las credenciales en `.env`:
   ```bash
   cat .env | grep ADMIN_DEFAULT
   ```

3. Si cambiaste las credenciales, reinicia el backend

### Las aplicaciones no se cargan en el portal

**Problema:** El portal muestra "No se encontraron aplicaciones"

**Solución:**
1. Verifica que el backend esté ejecutándose
2. Verifica las aplicaciones registradas:
   ```bash
   curl http://localhost:8601/api/apps
   ```
3. Si no hay aplicaciones, regístralas desde el panel de admin

### Error de conexión al backend

**Problema:** "No se pudo conectar al backend"

**Solución:**
1. Verifica que existe el archivo `.env`:
   ```bash
   ls -la .env
   ```
   Si no existe, crea uno:
   ```bash
   cp .env.example .env
   ```

2. Verifica la variable `BACKEND_BASE_URL` en `.env`:
   ```
   BACKEND_BASE_URL=http://localhost:8601
   ```

3. Reinicia el backend y el portal

## 📝 API REST (uso avanzado)

### Login desde la línea de comandos

```bash
# Login
curl -c cookies.txt -X POST http://localhost:8601/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Listar todas las aplicaciones (admin)
curl -b cookies.txt http://localhost:8601/api/admin/apps | python3 -m json.tool

# Crear una aplicación
curl -b cookies.txt -X POST http://localhost:8601/api/admin/apps \
  -H "Content-Type: application/json" \
  -d '{
    "id": "app_test",
    "name": "App de Prueba",
    "description": "Aplicación de prueba",
    "path": "/apps/test",
    "tags": "test,demo",
    "enabled": true,
    "access_mode": "public"
  }'
```

## 🔒 Seguridad

### Cambiar credenciales de administrador

1. Edita el archivo `.env`:
   ```bash
   nano .env
   ```

2. Modifica las líneas:
   ```env
   ADMIN_DEFAULT_USER=tu_nuevo_usuario
   ADMIN_DEFAULT_PASS=tu_nueva_contraseña_segura
   ```

3. Reinicia el backend:
   ```bash
   pkill -f uvicorn
   cd backend && ./run_local.sh
   ```

### Cambiar SECRET_KEY

Para mayor seguridad, cambia el `SECRET_KEY` en `.env`:

```bash
# Generar una clave aleatoria
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Copia el resultado y actualiza .env:
SECRET_KEY=tu_clave_aleatoria_generada
```

## 💡 Comandos Útiles

```bash
# Ver logs del backend
tail -f /tmp/backend.log

# Ver logs del portal
tail -f /tmp/portal.log

# Detener todo el sistema
pkill -f uvicorn && pkill -f streamlit

# Verificar puertos en uso
lsof -i :8601  # Backend
lsof -i :8600  # Portal

# Reiniciar backend
cd backend
pkill -f uvicorn
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8601 --reload

# Reiniciar portal
cd portal
pkill -f streamlit
source venv/bin/activate
streamlit run app/portal.py --server.port=8600 --server.baseUrlPath=/portal
```

## 📞 Soporte

Si tienes problemas:

1. Revisa los logs:
   - Backend: `/tmp/backend.log`
   - Portal: `/tmp/portal.log`

2. Verifica que todos los servicios estén corriendo:
   ```bash
   ps aux | grep -E "uvicorn|streamlit"
   ```

3. Consulta el README principal del proyecto

---

**Fecha de última actualización:** 2025-11-07
**Versión:** 2.0.0
