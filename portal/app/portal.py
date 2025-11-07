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
    page_title="Automation Suite Portal",
    page_icon="🔷",
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

        # Estilo del botón con CSS personalizado - Diseño azul profesional
        st.markdown(f"""
            <style>
            .app-card-{app_id} {{
                background: linear-gradient(135deg, #1E88E5 0%, #1976D2 50%, #1565C0 100%);
                border-radius: 16px;
                padding: 32px 24px;
                text-align: center;
                margin: 12px 0;
                box-shadow: 0 4px 16px rgba(30, 136, 229, 0.25);
                transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
            .app-card-{app_id}:hover {{
                transform: translateY(-8px) scale(1.02);
                box-shadow: 0 12px 32px rgba(30, 136, 229, 0.4);
                border-color: rgba(255, 255, 255, 0.2);
            }}
            .app-icon {{
                font-size: 60px;
                margin-bottom: 16px;
                filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
            }}
            .app-title {{
                color: white;
                font-size: 22px;
                font-weight: 700;
                margin: 12px 0 10px 0;
                letter-spacing: -0.01em;
                font-family: 'Inter', 'Roboto', -apple-system, sans-serif;
            }}
            .app-description {{
                color: rgba(255, 255, 255, 0.92);
                font-size: 14px;
                line-height: 1.6;
                margin-bottom: 16px;
                font-family: 'Inter', 'Roboto', -apple-system, sans-serif;
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
                background: #f8f9fa;
                border: 2px dashed #cbd5e0;
                border-radius: 16px;
                padding: 32px 24px;
                text-align: center;
                margin: 12px 0;
                opacity: 0.7;
            }}
            .app-icon-disabled {{
                font-size: 60px;
                margin-bottom: 16px;
                filter: grayscale(100%);
                opacity: 0.5;
            }}
            .app-title-disabled {{
                color: #64748b;
                font-size: 22px;
                font-weight: 600;
                margin: 12px 0 10px 0;
                font-family: 'Inter', 'Roboto', -apple-system, sans-serif;
            }}
            .app-description-disabled {{
                color: #94a3b8;
                font-size: 14px;
                line-height: 1.6;
                margin-bottom: 16px;
                font-family: 'Inter', 'Roboto', -apple-system, sans-serif;
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
    # Estilo global minimalista y profesional
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        * {
            font-family: 'Inter', 'Roboto', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        .main {
            background-color: #f7fafc;
        }

        .main-header {
            text-align: center;
            padding: 48px 0 32px 0;
            background: linear-gradient(180deg, #ffffff 0%, #f7fafc 100%);
            border-bottom: 1px solid #e2e8f0;
            margin: -20px -40px 40px -40px;
            position: sticky;
            top: 0;
            z-index: 999;
            backdrop-filter: blur(10px);
        }

        .logo-container {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 16px;
            margin-bottom: 12px;
        }

        .logo-icon {
            font-size: 56px;
            filter: drop-shadow(0 4px 6px rgba(30, 136, 229, 0.3));
        }

        .main-title {
            font-size: 42px;
            font-weight: 800;
            background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 8px;
            letter-spacing: -0.02em;
        }

        .main-subtitle {
            font-size: 17px;
            color: #64748b;
            font-weight: 500;
            letter-spacing: -0.01em;
        }

        .stButton > button {
            height: 56px;
            font-size: 16px;
            font-weight: 600;
            border-radius: 12px;
            transition: all 0.3s ease;
            font-family: 'Inter', sans-serif;
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 16px rgba(30, 136, 229, 0.3);
        }

        [data-testid="stExpander"] {
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            background: white;
        }
        </style>
    """, unsafe_allow_html=True)

    # Cabecera con logo y título
    st.markdown("""
        <div class="main-header">
            <div class="logo-container">
                <div class="logo-icon">🔷</div>
            </div>
            <div class="main-title">Automation Suite Portal</div>
            <div class="main-subtitle">Plataforma Corporativa de Automatización</div>
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

    # Footer profesional
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
        <style>
        .footer {
            text-align: center;
            color: #94a3b8;
            font-size: 13px;
            padding: 24px 0;
            margin-top: 40px;
            border-top: 1px solid #e2e8f0;
            font-family: 'Inter', sans-serif;
            letter-spacing: 0.01em;
        }
        </style>
        <div class="footer">
            © Forvis Mazars Automation Suite – 2025
        </div>
    """, unsafe_allow_html=True)


# ===========================
# Punto de Entrada
# ===========================

if __name__ == "__main__":
    main()
