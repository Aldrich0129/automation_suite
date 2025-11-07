#!/bin/bash
# Script de Inicio del Sistema - Automation Suite
# ================================================
# Este script facilita el inicio de todo el sistema

set -e

echo "╔═══════════════════════════════════════════════════════╗"
echo "║       🚀 AUTOMATION SUITE - INICIO DEL SISTEMA       ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Verificar archivo .env
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Error: No existe el archivo .env${NC}"
    echo ""
    echo "Creando archivo .env desde .env.example..."
    cp .env.example .env
    echo -e "${GREEN}✅ Archivo .env creado${NC}"
    echo ""
fi

# Función para verificar si un puerto está en uso
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0
    else
        return 1
    fi
}

# Función para iniciar el backend
start_backend() {
    echo -e "${BLUE}📦 Iniciando Backend...${NC}"
    cd backend

    # Crear entorno virtual si no existe
    if [ ! -d "venv" ]; then
        echo "  Creando entorno virtual..."
        python3 -m venv venv
    fi

    # Activar entorno y instalar dependencias
    source venv/bin/activate
    pip install -q -r requirements.txt

    # Ejecutar migraciones
    echo "  Ejecutando migraciones..."
    alembic upgrade head >/dev/null 2>&1

    # Iniciar servidor en background
    echo "  Iniciando servidor..."
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8601 > /tmp/backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > /tmp/backend.pid

    cd ..

    # Esperar a que el backend esté listo
    echo "  Esperando a que el backend esté disponible..."
    for i in {1..10}; do
        if curl -s http://localhost:8601/api/healthz >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Backend iniciado correctamente (PID: $BACKEND_PID)${NC}"
            return 0
        fi
        sleep 1
    done

    echo -e "${RED}❌ Error: El backend no respondió${NC}"
    return 1
}

# Función para iniciar el portal
start_portal() {
    echo -e "${BLUE}🌐 Iniciando Portal...${NC}"
    cd portal

    # Crear entorno virtual si no existe
    if [ ! -d "venv" ]; then
        echo "  Creando entorno virtual..."
        python3 -m venv venv
    fi

    # Activar entorno y instalar dependencias
    source venv/bin/activate
    pip install -q -r requirements.txt

    # Iniciar streamlit en background
    echo "  Iniciando servidor..."
    nohup streamlit run app/portal.py --server.port=8600 --server.baseUrlPath=/portal > /tmp/portal.log 2>&1 &
    PORTAL_PID=$!
    echo $PORTAL_PID > /tmp/portal.pid

    cd ..

    echo -e "${GREEN}✅ Portal iniciado correctamente (PID: $PORTAL_PID)${NC}"
}

# Función para detener el sistema
stop_system() {
    echo ""
    echo -e "${YELLOW}🛑 Deteniendo sistema...${NC}"

    if [ -f "/tmp/backend.pid" ]; then
        BACKEND_PID=$(cat /tmp/backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill $BACKEND_PID
            echo "  Backend detenido"
        fi
        rm /tmp/backend.pid
    fi

    if [ -f "/tmp/portal.pid" ]; then
        PORTAL_PID=$(cat /tmp/portal.pid)
        if kill -0 $PORTAL_PID 2>/dev/null; then
            kill $PORTAL_PID
            echo "  Portal detenido"
        fi
        rm /tmp/portal.pid
    fi

    # Limpiar procesos zombies
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    pkill -f "streamlit run app/portal.py" 2>/dev/null || true

    echo -e "${GREEN}✅ Sistema detenido${NC}"
}

# Verificar si ya hay servicios corriendo
if check_port 8601; then
    echo -e "${YELLOW}⚠️  El puerto 8601 ya está en uso${NC}"
    echo "¿Desea detener el backend existente? (s/n)"
    read -r response
    if [[ "$response" =~ ^[Ss]$ ]]; then
        pkill -f "uvicorn app.main:app" || true
        sleep 2
    else
        echo "Usando backend existente"
    fi
fi

if check_port 8600; then
    echo -e "${YELLOW}⚠️  El puerto 8600 ya está en uso${NC}"
    echo "¿Desea detener el portal existente? (s/n)"
    read -r response
    if [[ "$response" =~ ^[Ss]$ ]]; then
        pkill -f "streamlit run app/portal.py" || true
        sleep 2
    else
        echo "Usando portal existente"
    fi
fi

# Iniciar servicios
if ! check_port 8601; then
    start_backend
else
    echo -e "${GREEN}✅ Backend ya está ejecutándose${NC}"
fi

echo ""

if ! check_port 8600; then
    start_portal
else
    echo -e "${GREEN}✅ Portal ya está ejecutándose${NC}"
fi

echo ""
echo "╔═══════════════════════════════════════════════════════╗"
echo "║            ✅ SISTEMA INICIADO CORRECTAMENTE          ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}🌐 URLs de Acceso:${NC}"
echo "  • Backend API:    http://localhost:8601"
echo "  • Backend Docs:   http://localhost:8601/docs"
echo "  • Portal:         http://localhost:8600/portal"
echo ""
echo -e "${GREEN}🔐 Credenciales de Administrador:${NC}"
echo "  • Usuario:    admin"
echo "  • Contraseña: admin123"
echo ""
echo -e "${BLUE}📝 Para acceder al panel de administración:${NC}"
echo "  1. Abre http://localhost:8600/portal en tu navegador"
echo "  2. Ve a la pestaña '⚙️ Administración'"
echo "  3. Inicia sesión con las credenciales de arriba"
echo ""
echo -e "${YELLOW}📊 Aplicaciones disponibles: 4${NC}"
echo "  • Gestión de Inventarios"
echo "  • Procesamiento de Facturas"
echo "  • Generador de Reportes"
echo "  • Generador de Carta de Manifestación"
echo ""
echo -e "${BLUE}💡 Comandos útiles:${NC}"
echo "  • Ver logs del backend:  tail -f /tmp/backend.log"
echo "  • Ver logs del portal:   tail -f /tmp/portal.log"
echo "  • Detener sistema:       pkill -f uvicorn && pkill -f streamlit"
echo ""
echo -e "${GREEN}¡Listo para usar! 🎉${NC}"
echo ""

# Trap para detener el sistema al salir
trap stop_system EXIT INT TERM
