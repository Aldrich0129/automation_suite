#!/bin/bash
# Script para ejecutar la app localmente
# ========================================

# Variables de configuración
APP_PORT=8601
BASE_URL_PATH="/app_carta_manifestacion"
BACKEND_URL=${BACKEND_BASE_URL:-"http://localhost:8000"}

echo "========================================"
echo "Generador de Cartas de Manifestación"
echo "========================================"
echo ""
echo "Puerto: $APP_PORT"
echo "Ruta base: $BASE_URL_PATH"
echo "Backend URL: $BACKEND_URL"
echo ""
echo "Accede a la app en:"
echo "  http://localhost:$APP_PORT$BASE_URL_PATH"
echo ""
echo "========================================"
echo ""

# Exportar variables de entorno
export BACKEND_BASE_URL=$BACKEND_URL

# Ejecutar Streamlit
streamlit run app/ui.py \
  --server.port=$APP_PORT \
  --server.baseUrlPath=$BASE_URL_PATH
