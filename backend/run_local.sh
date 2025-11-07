#!/bin/bash
# Script para ejecutar el backend localmente

set -e

echo "🚀 Iniciando Backend - Automation Suite"
echo "========================================"

# Verificar que estamos en el directorio correcto
if [ ! -f "app/main.py" ]; then
    echo "❌ Error: Ejecuta este script desde el directorio backend/"
    exit 1
fi

# Verificar archivo .env
if [ ! -f "../.env" ]; then
    echo "⚠️  Advertencia: No se encontró archivo .env"
    echo "   Copia .env.example a .env y configura las variables"
fi

# Instalar dependencias si es necesario
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
fi

echo "📦 Activando entorno virtual..."
source venv/bin/activate

echo "📦 Instalando dependencias..."
pip install -r requirements.txt

echo "🗄️  Ejecutando migraciones..."
if [ -f "alembic.ini" ]; then
    alembic upgrade head
fi

echo "✅ Backend listo"
echo ""
echo "🌐 Servidor escuchando en http://localhost:8000"
echo "📖 Documentación en http://localhost:8000/docs"
echo ""

# Ejecutar servidor
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
