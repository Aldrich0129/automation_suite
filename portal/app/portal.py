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
from datetime import datetime
import time

import streamlit as st

# Importar cliente HTTP y panel admin
try:
    from client import BackendClient
except ImportError:
    BackendClient = None

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
    page_icon="🔵",  # Círculo azul simple, sin emoji complejo
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ===========================
# Funciones Auxiliares
# ===========================

@st.cache_data(ttl=15)
def load_apps_from_backend() -> List[Dict]:
    """
    Carga el catálogo de aplicaciones desde el backend.

    Returns:
        List[Dict]: Lista de aplicaciones desde GET /api/apps
    """
    if BackendClient is None:
        st.error("No se pudo importar el cliente HTTP")
        return []

    try:
        client = BackendClient()
        apps = client.list_apps()

        # Convertir tags de string separado por comas a lista
        for app in apps:
            if isinstance(app.get('tags'), str):
                app['tags'] = [tag.strip() for tag in app['tags'].split(',') if tag.strip()]
            elif not app.get('tags'):
                app['tags'] = []

        return apps
    except Exception as e:
        st.error(f"Error al cargar aplicaciones desde el backend: {str(e)}")
        st.info("Verifica que el backend esté ejecutándose en la URL configurada")
        return []


def get_category_color(tags: List[str]) -> str:
    """
    Retorna un color de categoría basado en las etiquetas de la aplicación.

    Args:
        tags (List[str]): Lista de etiquetas de la aplicación

    Returns:
        str: Código de color hexadecimal
    """
    # Devuelve el color primario por defecto
    return '#1E88E5'


def render_app_card(app: Dict, backend_url: str):
    """
    Renderiza una tarjeta minimalista y corporativa para una aplicación.
    Diseño con CTA unificado (card completa clicable).

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
    access_mode = app.get('access_mode', 'public')

    # Crear contenedor con estilo minimalista
    if app_enabled:
        full_url = f"{backend_url}{app_path}"

        # Para acceso público, renderizar card clicable
        if access_mode == "public":
            st.markdown(f"""
                <a href="{full_url}"
                   target="_self"
                   class="app-card app-card-clickable"
                   aria-label="Abrir {app_name}"
                   data-app-id="{app_id}">
                    <div class="app-card-body">
                        <h3 class="app-card-title">{app_name}</h3>
                        <p class="app-card-description">{app_description}</p>
                    </div>
                    <div class="app-card-cta">
                        <span class="app-card-cta-text">Abrir</span>
                        <svg class="app-card-cta-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <path d="M6 3L11 8L6 13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </div>
                </a>
            """, unsafe_allow_html=True)

        elif access_mode == "password":
            # Para password, mostrar card que abre modal
            st.markdown(f"""
                <div class="app-card app-card-protected" data-app-id="{app_id}">
                    <div class="app-card-body">
                        <div class="app-card-lock-badge">Protegido</div>
                        <h3 class="app-card-title">{app_name}</h3>
                        <p class="app-card-description">{app_description}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Botón para abrir modal
            if st.button(
                "Acceder con contraseña",
                key=f"btn_{app_id}",
                use_container_width=True,
                type="primary"
            ):
                st.session_state[f"show_password_modal_{app_id}"] = True
                st.rerun()

            # Modal de contraseña
            if st.session_state.get(f"show_password_modal_{app_id}", False):
                with st.form(f"password_modal_{app_id}"):
                    st.markdown("**Ingresa la contraseña para acceder**")
                    password = st.text_input("Contraseña", type="password", key=f"pwd_{app_id}")

                    col1, col2 = st.columns(2)

                    with col1:
                        submit = st.form_submit_button("Acceder", use_container_width=True)

                    with col2:
                        cancel = st.form_submit_button("Cancelar", use_container_width=True)

                    if cancel:
                        st.session_state[f"show_password_modal_{app_id}"] = False
                        st.rerun()

                    if submit:
                        if password:
                            try:
                                client = BackendClient()
                                access_granted = client.check_app_access(app_id, password)

                                if access_granted:
                                    st.session_state[f"show_password_modal_{app_id}"] = False
                                    st.markdown(
                                        f'<meta http-equiv="refresh" content="0; url={full_url}">',
                                        unsafe_allow_html=True
                                    )
                                    st.success(f"Acceso concedido. Redirigiendo a {app_name}...")
                                else:
                                    st.error("Contraseña incorrecta")
                            except Exception as e:
                                st.error(f"Error al verificar acceso: {str(e)}")
                        else:
                            st.warning("Ingresa la contraseña")

        elif access_mode == "sso":
            # SSO - card deshabilitada
            st.markdown(f"""
                <div class="app-card app-card-disabled" data-app-id="{app_id}">
                    <div class="app-card-body">
                        <div class="app-card-lock-badge">SSO</div>
                        <h3 class="app-card-title">{app_name}</h3>
                        <p class="app-card-description">{app_description}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            st.info("SSO en desarrollo. Contacta al administrador.")
    else:
        # Aplicación desactivada
        st.markdown(f"""
            <div class="app-card app-card-inactive" data-app-id="{app_id}">
                <div class="app-card-body">
                    <div class="app-card-status-badge">En desarrollo</div>
                    <h3 class="app-card-title app-card-title-inactive">{app_name}</h3>
                    <p class="app-card-description app-card-description-inactive">{app_description}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)


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
        st.metric("Total de Aplicaciones", total_apps)

    with col2:
        st.metric("Aplicaciones Activas", enabled_apps)

    with col3:
        st.metric("Aplicaciones Inactivas", disabled_apps)


# ===========================
# Interfaz Principal
# ===========================

def main():
    """
    Función principal que renderiza la interfaz del portal.
    """
    # Navegación principal con tabs
    if show_admin_panel is not None:
        tab1, tab2 = st.tabs(["Portal", "Administración"])

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
    # CSS Global - Tema Corporativo Minimalista
    st.markdown("""
        <style>
        /* ===========================
           SISTEMA DE DISEÑO CORPORATIVO
           ========================== */

        /* Variables de Color */
        :root {
            --color-primary: #1E88E5;
            --color-primary-hover: #1565C0;
            --color-border: #E6EAF0;
            --color-bg-page: #F7F9FC;
            --color-text-primary: #0F172A;
            --color-text-secondary: #475569;
            --color-white: #FFFFFF;
            --color-shadow: rgba(30, 136, 229, 0.12);
            --color-shadow-hover: rgba(30, 136, 229, 0.24);
        }

        /* Tipografía - System Fonts Stack */
        * {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        }

        /* Fondo Global */
        .main {
            background-color: var(--color-bg-page);
        }

        /* ===========================
           HEADER
           ========================== */
        .main-header {
            text-align: center;
            padding: 56px 0 40px 0;
            background: var(--color-white);
            border-bottom: 1px solid var(--color-border);
            margin: -20px -40px 48px -40px;
        }

        .main-title {
            font-size: 36px;
            font-weight: 600;
            color: var(--color-text-primary);
            margin-bottom: 8px;
            letter-spacing: -0.02em;
        }

        .main-subtitle {
            font-size: 16px;
            color: var(--color-text-secondary);
            font-weight: 400;
            letter-spacing: 0;
        }

        /* ===========================
           APP CARDS - CTA UNIFICADO
           ========================== */

        /* Card Base */
        .app-card {
            position: relative;
            display: block;
            background: var(--color-primary);
            border-radius: 20px;
            padding: 32px 28px;
            margin: 0 0 28px 0;
            box-shadow: 0 2px 8px var(--color-shadow);
            transition: all 240ms cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid transparent;
            text-decoration: none;
            cursor: default;
        }

        /* Card Clicable (acceso público) */
        .app-card-clickable {
            cursor: pointer;
        }

        .app-card-clickable:hover {
            transform: translateY(-6px);
            box-shadow: 0 8px 24px var(--color-shadow-hover);
            background: var(--color-primary-hover);
            border-color: rgba(255, 255, 255, 0.15);
        }

        .app-card-clickable:focus {
            outline: 3px solid var(--color-primary);
            outline-offset: 4px;
        }

        /* Card Body */
        .app-card-body {
            position: relative;
            z-index: 1;
        }

        /* Card Title */
        .app-card-title {
            font-size: 22px;
            font-weight: 600;
            color: var(--color-white);
            margin: 0 0 12px 0;
            line-height: 1.3;
            letter-spacing: -0.01em;
        }

        /* Card Description */
        .app-card-description {
            font-size: 15px;
            color: rgba(255, 255, 255, 0.90);
            line-height: 1.6;
            margin: 0;
        }

        /* CTA Chip (esquina inferior derecha) */
        .app-card-cta {
            position: absolute;
            bottom: 24px;
            right: 24px;
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 8px 16px;
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(8px);
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            transition: all 240ms ease;
        }

        .app-card-clickable:hover .app-card-cta {
            background: rgba(255, 255, 255, 0.3);
            border-color: rgba(255, 255, 255, 0.5);
        }

        .app-card-cta-text {
            font-size: 13px;
            font-weight: 600;
            color: var(--color-white);
            letter-spacing: 0.02em;
        }

        .app-card-cta-icon {
            color: var(--color-white);
        }

        /* Badge para apps protegidas */
        .app-card-lock-badge,
        .app-card-status-badge {
            display: inline-block;
            padding: 4px 12px;
            background: rgba(255, 255, 255, 0.25);
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            color: var(--color-white);
            margin-bottom: 16px;
            letter-spacing: 0.03em;
        }

        /* Cards Protegidas */
        .app-card-protected {
            background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%);
        }

        /* Cards Deshabilitadas */
        .app-card-disabled {
            background: #94A3B8;
            opacity: 0.7;
        }

        /* Cards Inactivas (en desarrollo) */
        .app-card-inactive {
            background: #F1F5F9;
            border: 2px dashed var(--color-border);
            box-shadow: none;
        }

        .app-card-title-inactive {
            color: var(--color-text-secondary);
        }

        .app-card-description-inactive {
            color: #94A3B8;
        }

        .app-card-status-badge {
            background: var(--color-border);
            color: var(--color-text-secondary);
        }

        /* ===========================
           STREAMLIT OVERRIDES
           ========================== */

        /* Botones de Streamlit */
        .stButton > button {
            height: 48px;
            font-size: 15px;
            font-weight: 600;
            border-radius: 12px;
            transition: all 200ms ease;
            border: none;
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px var(--color-shadow-hover);
        }

        .stButton > button:focus {
            outline: 3px solid var(--color-primary);
            outline-offset: 2px;
        }

        /* Expanders */
        [data-testid="stExpander"] {
            border-radius: 12px;
            border: 1px solid var(--color-border);
            background: var(--color-white);
        }

        /* Tabs del Admin */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background: var(--color-white);
            padding: 12px;
            border-radius: 12px;
            border: 1px solid var(--color-border);
        }

        .stTabs [data-baseweb="tab"] {
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 600;
        }

        /* ===========================
           FOOTER
           ========================== */
        .portal-footer {
            text-align: center;
            color: var(--color-text-secondary);
            font-size: 13px;
            padding: 32px 0;
            margin-top: 64px;
            border-top: 1px solid var(--color-border);
            letter-spacing: 0;
        }

        /* ===========================
           RESPONSIVE GRID
           ========================== */
        [data-testid="column"] {
            gap: 28px;
        }

        /* ===========================
           ACCESIBILIDAD
           ========================== */
        *:focus-visible {
            outline: 3px solid var(--color-primary);
            outline-offset: 2px;
        }

        /* Contraste mínimo AA para textos */
        .app-card-description,
        .app-card-cta-text {
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        }
        </style>
    """, unsafe_allow_html=True)

    # Cabecera minimalista sin emojis
    st.markdown("""
        <div class="main-header">
            <h1 class="main-title">Automation Suite Portal</h1>
            <p class="main-subtitle">Plataforma Corporativa de Automatización</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Cargar configuración
    backend_url = get_backend_base_url()

    # Cargar el inventario de aplicaciones desde el backend
    with st.spinner("Cargando catálogo de aplicaciones..."):
        apps = load_apps_from_backend()

    # Mostrar aplicaciones
    if not apps:
        st.warning("No se encontraron aplicaciones registradas.")
        st.info(
            "**Sugerencia:** Ve a la pestaña 'Administración' para crear aplicaciones, "
            "o verifica que el backend esté ejecutándose correctamente."
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
            with st.expander(f"Aplicaciones en Desarrollo ({len(inactive_apps)})"):
                num_cols = 3
                for i in range(0, len(inactive_apps), num_cols):
                    cols = st.columns(num_cols)
                    for j, col in enumerate(cols):
                        idx = i + j
                        if idx < len(inactive_apps):
                            with col:
                                render_app_card(inactive_apps[idx], backend_url)

    # Footer corporativo minimalista
    st.markdown("""
        <div class="portal-footer">
            © Forvis Mazars Automation Suite – 2025
        </div>
    """, unsafe_allow_html=True)


# ===========================
# Punto de Entrada
# ===========================

if __name__ == "__main__":
    main()
