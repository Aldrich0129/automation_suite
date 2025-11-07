"""
Panel de Administración - Portal Automation Suite
==================================================

Gestión de aplicaciones, accesos y métricas.
"""

import streamlit as st
from datetime import datetime
from typing import Optional
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from client import BackendClient


# ===========================
# Inicialización
# ===========================

def init_admin_session():
    """Inicializa variables de sesión para el admin."""
    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False
    if "admin_username" not in st.session_state:
        st.session_state.admin_username = None


# ===========================
# Login
# ===========================

def show_login_page():
    """Muestra la página de login de administrador."""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        </style>
        <div style="text-align: center; padding: 48px 0; font-family: 'Inter', sans-serif;">
            <div style="font-size: 48px; margin-bottom: 16px;">🔐</div>
            <h1 style="background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%);
                       -webkit-background-clip: text;
                       -webkit-text-fill-color: transparent;
                       background-clip: text;
                       font-weight: 800;
                       font-size: 36px;
                       margin-bottom: 12px;">
                Panel de Administración
            </h1>
            <p style="color: #64748b; font-size: 16px; font-weight: 500;">Ingresa tus credenciales para continuar</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        with st.form("login_form"):
            username = st.text_input("Usuario", placeholder="admin")
            password = st.text_input("Contraseña", type="password", placeholder="••••••••")
            submit = st.form_submit_button("Iniciar Sesión", use_container_width=True)

            if submit:
                if not username or not password:
                    st.error("❌ Por favor completa todos los campos")
                    return

                try:
                    client = BackendClient()
                    response = client.login(username, password)

                    st.session_state.admin_logged_in = True
                    st.session_state.admin_username = username
                    st.success("✅ Sesión iniciada correctamente")
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error al iniciar sesión: {str(e)}")


def show_logout():
    """Muestra botón de logout."""
    col1, col2 = st.columns([4, 1])

    with col2:
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            try:
                client = BackendClient()
                client.logout()
            except Exception:
                pass

            st.session_state.admin_logged_in = False
            st.session_state.admin_username = None
            st.rerun()


# ===========================
# Gestión de Aplicaciones
# ===========================

def show_apps_management():
    """Muestra la página de gestión de aplicaciones."""
    st.markdown("## 📦 Gestión de Aplicaciones")
    st.markdown("---")

    client = BackendClient()

    # Botón para crear nueva app
    col1, col2 = st.columns([3, 1])

    with col2:
        if st.button("➕ Nueva Aplicación", use_container_width=True):
            st.session_state.show_create_app = True

    # Formulario de creación
    if st.session_state.get("show_create_app", False):
        with st.expander("✏️ Crear Nueva Aplicación", expanded=True):
            with st.form("create_app_form"):
                col1, col2 = st.columns(2)

                with col1:
                    app_id = st.text_input("ID *", placeholder="app_ejemplo")
                    app_name = st.text_input("Nombre *", placeholder="Mi Aplicación")
                    app_path = st.text_input("Path *", placeholder="/apps/ejemplo")

                with col2:
                    app_description = st.text_area("Descripción", placeholder="Descripción de la aplicación")
                    app_tags = st.text_input("Tags", placeholder="tag1,tag2,tag3")
                    app_enabled = st.checkbox("Habilitada", value=True)

                access_mode = st.selectbox("Modo de Acceso", ["public", "password", "sso"])

                col_submit, col_cancel = st.columns(2)

                with col_submit:
                    submit = st.form_submit_button("✅ Crear", use_container_width=True)

                with col_cancel:
                    cancel = st.form_submit_button("❌ Cancelar", use_container_width=True)

                if cancel:
                    st.session_state.show_create_app = False
                    st.rerun()

                if submit:
                    if not app_id or not app_name or not app_path:
                        st.error("❌ Los campos ID, Nombre y Path son obligatorios")
                    else:
                        try:
                            app_data = {
                                "id": app_id,
                                "name": app_name,
                                "description": app_description,
                                "path": app_path,
                                "tags": app_tags,
                                "enabled": app_enabled,
                                "access_mode": access_mode
                            }

                            client.create_app(app_data)
                            st.success(f"✅ Aplicación '{app_name}' creada correctamente")
                            st.session_state.show_create_app = False
                            st.rerun()

                        except Exception as e:
                            st.error(f"❌ Error al crear aplicación: {str(e)}")

    # Lista de aplicaciones
    st.markdown("### Aplicaciones Existentes")

    try:
        apps = client.list_all_apps()

        if not apps:
            st.info("ℹ️ No hay aplicaciones registradas")
            return

        for app in apps:
            with st.expander(f"{'🟢' if app['enabled'] else '🔴'} {app['name']} ({app['id']})"):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"**ID:** `{app['id']}`")
                    st.markdown(f"**Path:** `{app['path']}`")
                    st.markdown(f"**Modo de acceso:** {app['access_mode']}")

                with col2:
                    st.markdown(f"**Habilitada:** {'✅ Sí' if app['enabled'] else '❌ No'}")
                    st.markdown(f"**Tags:** {app.get('tags', 'N/A')}")
                    if app.get('has_password'):
                        st.markdown("**Contraseña:** 🔒 Configurada")

                st.markdown(f"**Descripción:** {app.get('description', 'Sin descripción')}")

                # Acciones
                col_toggle, col_pass, col_del = st.columns(3)

                with col_toggle:
                    new_status = not app['enabled']
                    button_text = "✅ Activar" if new_status else "⏸ Desactivar"

                    if st.button(button_text, key=f"toggle_{app['id']}", use_container_width=True):
                        try:
                            client.update_app(app['id'], {"enabled": new_status})
                            st.success(f"Estado actualizado")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

                with col_pass:
                    if st.button("🔑 Contraseña", key=f"pass_{app['id']}", use_container_width=True):
                        st.session_state[f"show_password_{app['id']}"] = True
                        st.rerun()

                with col_del:
                    if st.button("🗑️ Eliminar", key=f"del_{app['id']}", use_container_width=True):
                        try:
                            client.delete_app(app['id'])
                            st.success("Aplicación eliminada")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

                # Formulario de contraseña
                if st.session_state.get(f"show_password_{app['id']}", False):
                    with st.form(f"password_form_{app['id']}"):
                        new_password = st.text_input("Nueva Contraseña", type="password")
                        col_save, col_remove = st.columns(2)

                        with col_save:
                            save = st.form_submit_button("💾 Guardar")

                        with col_remove:
                            remove = st.form_submit_button("🗑️ Eliminar Contraseña")

                        if save and new_password:
                            try:
                                client.set_app_password(app['id'], new_password)
                                st.success("Contraseña actualizada")
                                st.session_state[f"show_password_{app['id']}"] = False
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {str(e)}")

                        if remove:
                            try:
                                client.remove_app_password(app['id'])
                                st.success("Contraseña eliminada")
                                st.session_state[f"show_password_{app['id']}"] = False
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {str(e)}")

    except Exception as e:
        st.error(f"❌ Error al cargar aplicaciones: {str(e)}")


# ===========================
# Métricas y Estadísticas
# ===========================

def show_metrics():
    """Muestra la página de métricas."""
    st.markdown("## 📊 Métricas y Telemetría")
    st.markdown("---")

    client = BackendClient()

    # Selector de período
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        days = st.selectbox("Período", [7, 15, 30, 60, 90], index=2)

    # Obtener estadísticas
    try:
        summary = client.get_stats_summary(days=days)

        # Métricas globales
        st.markdown("### 📈 Resumen Global")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Total de Eventos", f"{summary['total_events']:,}")

        with col2:
            st.metric("Aplicaciones con Actividad", len(summary['apps']))

        st.markdown("---")

        # Gráfico de barras: eventos por app
        st.markdown("### 📊 Eventos por Aplicación")

        if summary['apps']:
            fig, ax = plt.subplots(figsize=(10, 6))

            app_names = [app['app_name'] for app in summary['apps']]
            event_counts = [app['total_events'] for app in summary['apps']]

            # Colores de la paleta azul profesional
            colors = ['#1E88E5', '#1976D2', '#1565C0', '#0D47A1', '#42A5F5']
            colors = colors * (len(app_names) // len(colors) + 1)

            ax.barh(app_names, event_counts, color=colors[:len(app_names)])
            ax.set_xlabel('Número de Eventos')
            ax.set_title(f'Eventos Totales por Aplicación (Últimos {days} días)')
            ax.grid(axis='x', alpha=0.3)

            plt.tight_layout()
            st.pyplot(fig)

            # Tabla detallada
            st.markdown("### 📋 Detalle por Tipo de Evento")

            for app in summary['apps']:
                with st.expander(f"{app['app_name']} - {app['total_events']} eventos"):
                    for event in app['events']:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**{event['event_type']}**")
                        with col2:
                            st.markdown(f"`{event['count']} eventos`")

        else:
            st.info("ℹ️ No hay eventos registrados en el período seleccionado")

        st.markdown("---")

        # Serie temporal
        st.markdown("### 📈 Serie Temporal")

        if summary['apps']:
            app_selector = st.selectbox(
                "Selecciona una aplicación",
                options=[app['app_id'] for app in summary['apps']],
                format_func=lambda x: next(app['app_name'] for app in summary['apps'] if app['app_id'] == x)
            )

            event_type = st.selectbox(
                "Tipo de evento",
                ["open", "generate_document", "error", "custom"]
            )

            try:
                time_series = client.get_app_time_series(app_selector, event_type, days)

                fig, ax = plt.subplots(figsize=(12, 5))

                dates = [datetime.fromisoformat(point['date']) for point in time_series['series']]
                counts = [point['count'] for point in time_series['series']]

                ax.plot(dates, counts, marker='o', linewidth=2, color='#1976D2', markersize=4)
                ax.fill_between(dates, counts, alpha=0.3, color='#1976D2')
                ax.set_xlabel('Fecha')
                ax.set_ylabel('Número de Eventos')
                ax.set_title(f"{time_series['app_name']} - {event_type} (Últimos {days} días)")
                ax.grid(alpha=0.3)

                # Formatear fechas en el eje X
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
                ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, days // 10)))
                plt.xticks(rotation=45)

                plt.tight_layout()
                st.pyplot(fig)

            except Exception as e:
                st.error(f"❌ Error al cargar serie temporal: {str(e)}")

    except Exception as e:
        st.error(f"❌ Error al cargar métricas: {str(e)}")


# ===========================
# Navegación Principal
# ===========================

def show_admin_panel():
    """Muestra el panel de administración completo."""
    init_admin_session()

    # Verificar login
    if not st.session_state.admin_logged_in:
        show_login_page()
        return

    # Estilos globales del panel admin
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        * {
            font-family: 'Inter', 'Roboto', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        .admin-header {
            background: linear-gradient(180deg, #ffffff 0%, #f7fafc 100%);
            border-bottom: 1px solid #e2e8f0;
            padding: 24px 0;
            margin: -20px -40px 32px -40px;
            padding-left: 40px;
            padding-right: 40px;
        }

        .admin-title {
            font-size: 32px;
            font-weight: 800;
            background: linear-gradient(135deg, #0D47A1 0%, #1565C0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -0.02em;
            margin-bottom: 8px;
        }

        .admin-welcome {
            color: #64748b;
            font-size: 15px;
            font-weight: 500;
        }

        [data-testid="stExpander"] {
            background: white;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header con logout
    col1, col2 = st.columns([4, 1])

    with col1:
        st.markdown(f"""
            <div class="admin-header">
                <div class="admin-title">⚙️ Panel de Administración</div>
                <div class="admin-welcome">Bienvenido, <strong>{st.session_state.admin_username}</strong></div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.admin_logged_in = False
            st.session_state.admin_username = None
            st.rerun()

    st.markdown("---")

    # Menú de navegación
    tab1, tab2 = st.tabs(["📦 Aplicaciones", "📊 Métricas"])

    with tab1:
        show_apps_management()

    with tab2:
        show_metrics()
