#!/bin/bash
# Script para ejecutar el portal localmente

set -e

echo "🌐 Iniciando Portal - Automation Suite"
echo "======================================="

# Verificar que estamos en el directorio correcto
if [ ! -f "app/portal.py" ]; then
    echo "❌ Error: Ejecuta este script desde el directorio portal/"
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

echo "✅ Portal listo"
echo ""
echo "🌐 Portal disponible en http://localhost:8600/portal"
echo "⚙️  Acceso admin en http://localhost:8600/portal (pestaña Admin)"
echo ""

# Ejecutar portal
streamlit run app/portal.py --server.port=8600 --server.baseUrlPath=/portal
