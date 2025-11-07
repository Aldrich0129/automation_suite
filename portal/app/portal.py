"""
Portal Principal - Automation Suite
=====================================

Este es el punto de entrada principal de la suite de automatización corporativa.
Muestra un inventario de todas las aplicaciones disponibles y permite
navegar hacia cada una de ellas.

Funcionalidades:
- Carga del inventario de apps desde apps_registry.yaml
- Visualización de apps en formato de cuadrícula
- Redirección a las URLs de las aplicaciones
- Filtrado por estado (activada/desactivada)
- Visualización de etiquetas por aplicación

Uso:
    streamlit run portal/app/portal.py --server.port=8501 --server.baseUrlPath=/portal
"""

import os
import sys
from pathlib import Path
from typing import Dict, List

import streamlit as st
import yaml

# Añadir el directorio core al path para poder importar el módulo
CORE_PATH = Path(__file__).parent.parent.parent / "core"
sys.path.insert(0, str(CORE_PATH))

try:
    from core.settings import get_backend_base_url, get_portal_base_path
except ImportError:
    # Fallback si no se puede importar el módulo core
    def get_backend_base_url():
        return os.getenv("BACKEND_BASE_URL", "http://localhost:8601")

    def get_portal_base_path():
        return os.getenv("PORTAL_BASE_PATH", "/portal")


# ===========================
# Configuración de la Página
# ===========================

st.set_page_config(
    page_title="Automation Suite - Portal",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ===========================
# Funciones Auxiliares
# ===========================

def load_apps_registry(registry_path: str) -> List[Dict]:
    """
    Carga el inventario de aplicaciones desde el archivo YAML.

    Args:
        registry_path (str): Ruta al archivo apps_registry.yaml

    Returns:
        List[Dict]: Lista de aplicaciones con sus metadatos
    """
    try:
        with open(registry_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
            return data.get('apps', [])
    except FileNotFoundError:
        st.error(f"❌ No se encontró el archivo de registro: {registry_path}")
        return []
    except yaml.YAMLError as e:
        st.error(f"❌ Error al leer el archivo YAML: {e}")
        return []
    except Exception as e:
        st.error(f"❌ Error inesperado: {e}")
        return []


def render_app_card(app: Dict, backend_url: str):
    """
    Renderiza una tarjeta individual para una aplicación.

    Args:
        app (Dict): Diccionario con los datos de la aplicación
        backend_url (str): URL base del backend
    """
    app_id = app.get('id', 'N/A')
    app_name = app.get('name', 'Sin nombre')
    app_path = app.get('path', '/')
    app_tags = app.get('tags', [])
    app_enabled = app.get('enabled', False)

    # Crear el contenedor de la tarjeta
    with st.container():
        st.markdown("---")

        # Título de la aplicación
        st.subheader(f"📱 {app_name}")

        # Mostrar ID
        st.caption(f"**ID:** `{app_id}`")

        # Mostrar etiquetas si existen
        if app_tags:
            tags_text = " ".join([f"`{tag}`" for tag in app_tags])
            st.markdown(f"**Etiquetas:** {tags_text}")

        # Botón de acción según el estado
        if app_enabled:
            full_url = f"{backend_url}{app_path}"
            st.success("✅ **Estado:** Activada")

            # Botón para abrir la aplicación
            if st.button(
                "🚀 Abrir Aplicación",
                key=f"btn_{app_id}",
                use_container_width=True
            ):
                st.markdown(
                    f'<meta http-equiv="refresh" content="0; url={full_url}">',
                    unsafe_allow_html=True
                )
                st.info(f"Redirigiendo a: {full_url}")
        else:
            st.warning("⚠️ **Estado:** Desactivada")
            st.button(
                "❌ No Disponible",
                key=f"btn_{app_id}",
                disabled=True,
                use_container_width=True
            )


def render_statistics(apps: List[Dict]):
    """
    Renderiza estadísticas del inventario de aplicaciones.

    Args:
        apps (List[Dict]): Lista de aplicaciones
    """
    total_apps = len(apps)
    enabled_apps = sum(1 for app in apps if app.get('enabled', False))
    disabled_apps = total_apps - enabled_apps

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("📊 Total de Aplicaciones", total_apps)

    with col2:
        st.metric("✅ Aplicaciones Activas", enabled_apps)

    with col3:
        st.metric("⚠️ Aplicaciones Inactivas", disabled_apps)


# ===========================
# Interfaz Principal
# ===========================

def main():
    """
    Función principal que renderiza la interfaz del portal.
    """
    # Cabecera
    st.title("🏢 Automation Suite")
    st.subheader("Portal de Aplicaciones Corporativas")
    st.markdown("---")

    # Cargar configuración
    backend_url = get_backend_base_url()

    # Mostrar información de configuración (opcional, para debug)
    with st.expander("⚙️ Configuración del Sistema"):
        st.code(f"Backend URL: {backend_url}", language="text")
        st.code(f"Portal Base Path: {get_portal_base_path()}", language="text")

    # Cargar el inventario de aplicaciones
    registry_path = Path(__file__).parent.parent / "apps_registry.yaml"
    apps = load_apps_registry(str(registry_path))

    # Mostrar estadísticas
    if apps:
        st.markdown("### 📊 Estadísticas")
        render_statistics(apps)
        st.markdown("---")

    # Mostrar aplicaciones
    if not apps:
        st.warning("⚠️ No se encontraron aplicaciones registradas.")
        st.info(
            "💡 **Sugerencia:** Añade aplicaciones en el archivo "
            "`portal/apps_registry.yaml` para que aparezcan aquí."
        )
    else:
        st.markdown("### 📱 Aplicaciones Disponibles")

        # Filtro por estado
        filter_option = st.radio(
            "Filtrar por estado:",
            ["Todas", "Solo Activas", "Solo Inactivas"],
            horizontal=True,
            key="filter_status"
        )

        # Aplicar filtro
        filtered_apps = apps
        if filter_option == "Solo Activas":
            filtered_apps = [app for app in apps if app.get('enabled', False)]
        elif filter_option == "Solo Inactivas":
            filtered_apps = [app for app in apps if not app.get('enabled', False)]

        # Mostrar mensaje si no hay resultados
        if not filtered_apps:
            st.info(f"ℹ️ No hay aplicaciones para mostrar con el filtro: **{filter_option}**")
        else:
            # Renderizar aplicaciones en columnas (2 por fila)
            num_cols = 2
            for i in range(0, len(filtered_apps), num_cols):
                cols = st.columns(num_cols)
                for j, col in enumerate(cols):
                    idx = i + j
                    if idx < len(filtered_apps):
                        with col:
                            render_app_card(filtered_apps[idx], backend_url)

    # Footer
    st.markdown("---")
    st.caption(
        "🏢 **Automation Suite** v0.1.0 | "
        "Desarrollado para automatizaciones corporativas internas"
    )


# ===========================
# Punto de Entrada
# ===========================

if __name__ == "__main__":
    main()
