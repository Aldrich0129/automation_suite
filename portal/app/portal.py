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

# Importar panel admin
try:
    from admin_pages import show_admin_panel
except ImportError:
    show_admin_panel = None

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


def get_app_icon(tags: List[str]) -> str:
    """
    Retorna un icono apropiado basado en las etiquetas de la aplicación.

    Args:
        tags (List[str]): Lista de etiquetas de la aplicación

    Returns:
        str: Emoji representativo
    """
    icon_map = {
        'logística': '📦',
        'finanzas': '💰',
        'análisis': '📊',
        'reporting': '📈',
        'calidad': '✅',
        'inventario': '📦',
        'contabilidad': '💼',
        'validación': '🔍',
        'documentos': '📄',
        'métricas': '📉',
    }

    for tag in tags:
        if tag.lower() in icon_map:
            return icon_map[tag.lower()]

    return '🔧'


def render_app_card(app: Dict, backend_url: str):
    """
    Renderiza una tarjeta minimalista para una aplicación.

    Args:
        app (Dict): Diccionario con los datos de la aplicación
        backend_url (str): URL base del backend
    """
    app_id = app.get('id', 'N/A')
    app_name = app.get('name', 'Sin nombre')
    app_description = app.get('description', 'Sin descripción disponible')
    app_path = app.get('path', '/')
    app_tags = app.get('tags', [])
    app_enabled = app.get('enabled', False)

    # Obtener icono según las etiquetas
    icon = get_app_icon(app_tags)

    # Crear contenedor con estilo minimalista
    if app_enabled:
        full_url = f"{backend_url}{app_path}"

        # Estilo del botón con CSS personalizado - Colores modernos
        st.markdown(f"""
            <style>
            .app-card-{app_id} {{
                background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%);
                border-radius: 20px;
                padding: 28px 20px;
                text-align: center;
                margin: 12px 0;
                box-shadow: 0 4px 20px rgba(139, 92, 246, 0.3);
                transition: all 0.3s ease;
            }}
            .app-card-{app_id}:hover {{
                transform: translateY(-6px);
                box-shadow: 0 8px 30px rgba(139, 92, 246, 0.5);
            }}
            .app-icon {{
                font-size: 56px;
                margin-bottom: 12px;
            }}
            .app-title {{
                color: white;
                font-size: 20px;
                font-weight: 700;
                margin: 12px 0 8px 0;
                letter-spacing: -0.02em;
            }}
            .app-description {{
                color: rgba(255, 255, 255, 0.95);
                font-size: 13px;
                line-height: 1.6;
                margin-bottom: 16px;
            }}
            </style>
        """, unsafe_allow_html=True)

        # Contenedor de la tarjeta
        with st.container():
            st.markdown(f"""
                <div class="app-card-{app_id}">
                    <div class="app-icon">{icon}</div>
                    <div class="app-title">{app_name}</div>
                    <div class="app-description">{app_description}</div>
                </div>
            """, unsafe_allow_html=True)

            # Botón grande para abrir la aplicación
            if st.button(
                f"▶ Abrir {app_name}",
                key=f"btn_{app_id}",
                use_container_width=True,
                type="primary"
            ):
                st.markdown(
                    f'<meta http-equiv="refresh" content="0; url={full_url}">',
                    unsafe_allow_html=True
                )
                st.success(f"Redirigiendo a {app_name}...")
    else:
        # Aplicación desactivada - estilo más sutil
        st.markdown(f"""
            <style>
            .app-card-disabled-{app_id} {{
                background: #f5f5f5;
                border: 2px dashed #d0d0d0;
                border-radius: 16px;
                padding: 32px 24px;
                text-align: center;
                margin: 16px 0;
                opacity: 0.6;
            }}
            .app-icon-disabled {{
                font-size: 64px;
                margin-bottom: 16px;
                filter: grayscale(100%);
            }}
            .app-title-disabled {{
                color: #666;
                font-size: 24px;
                font-weight: 600;
                margin: 16px 0 8px 0;
            }}
            .app-description-disabled {{
                color: #888;
                font-size: 14px;
                line-height: 1.5;
                margin-bottom: 20px;
            }}
            </style>
        """, unsafe_allow_html=True)

        with st.container():
            st.markdown(f"""
                <div class="app-card-disabled-{app_id}">
                    <div class="app-icon-disabled">{icon}</div>
                    <div class="app-title-disabled">{app_name}</div>
                    <div class="app-description-disabled">{app_description}</div>
                </div>
            """, unsafe_allow_html=True)

            st.button(
                "⏸ No Disponible",
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
    # Navegación principal con tabs
    if show_admin_panel is not None:
        tab1, tab2 = st.tabs(["🏠 Portal", "⚙️ Administración"])

        with tab1:
            show_portal_content()

        with tab2:
            show_admin_panel()
    else:
        show_portal_content()


def show_portal_content():
    """
    Muestra el contenido principal del portal.
    """
    # Estilo global minimalista
    st.markdown("""
        <style>
        .main-header {
            text-align: center;
            padding: 40px 0 20px 0;
        }
        .main-title {
            font-size: 48px;
            font-weight: 800;
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 8px;
        }
        .main-subtitle {
            font-size: 18px;
            color: #64748b;
            font-weight: 500;
        }
        .stButton > button {
            height: 54px;
            font-size: 16px;
            font-weight: 600;
            border-radius: 14px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Cabecera minimalista
    st.markdown("""
        <div class="main-header">
            <div class="main-title">🏢 Automation Suite</div>
            <div class="main-subtitle">Plataforma de Automatización Corporativa</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Cargar configuración
    backend_url = get_backend_base_url()

    # Cargar el inventario de aplicaciones
    registry_path = Path(__file__).parent.parent / "apps_registry.yaml"
    apps = load_apps_registry(str(registry_path))

    # Mostrar aplicaciones
    if not apps:
        st.warning("⚠️ No se encontraron aplicaciones registradas.")
        st.info(
            "💡 **Sugerencia:** Añade aplicaciones en el archivo "
            "`portal/apps_registry.yaml` para que aparezcan aquí."
        )
    else:
        # Separar aplicaciones activas e inactivas
        active_apps = [app for app in apps if app.get('enabled', False)]
        inactive_apps = [app for app in apps if not app.get('enabled', False)]

        # Mostrar aplicaciones activas
        if active_apps:
            # Renderizar en cuadrícula de 3 columnas
            num_cols = 3
            for i in range(0, len(active_apps), num_cols):
                cols = st.columns(num_cols)
                for j, col in enumerate(cols):
                    idx = i + j
                    if idx < len(active_apps):
                        with col:
                            render_app_card(active_apps[idx], backend_url)

        # Mostrar aplicaciones inactivas en un expander
        if inactive_apps:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander(f"📋 Aplicaciones en Desarrollo ({len(inactive_apps)})"):
                num_cols = 3
                for i in range(0, len(inactive_apps), num_cols):
                    cols = st.columns(num_cols)
                    for j, col in enumerate(cols):
                        idx = i + j
                        if idx < len(inactive_apps):
                            with col:
                                render_app_card(inactive_apps[idx], backend_url)

    # Footer minimalista
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #a0aec0; font-size: 14px;'>"
        "Automation Suite v0.1.0 | Desarrollado para automatizaciones corporativas"
        "</div>",
        unsafe_allow_html=True
    )


# ===========================
# Punto de Entrada
# ===========================

if __name__ == "__main__":
    main()
