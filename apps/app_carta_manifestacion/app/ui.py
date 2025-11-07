"""
UI - App Carta Manifestación
=============================

Interfaz de usuario con Streamlit para generar cartas de manifestación.
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List

from services import CartaManifestacionService
from domain import (
    OFICINAS,
    CONDITIONAL_VARS_MAP,
    parse_date_string,
    set_spanish_locale
)

# Inicializar locale español
set_spanish_locale()

# Configuración de la página
st.set_page_config(
    page_title="Generador de Cartas de Manifestación",
    page_icon="📄",
    layout="wide"
)

# Título principal
st.title("Generador de Cartas de Manifestación")
st.markdown("---")


def render_office_section(var_values: Dict, imported_data: Dict) -> None:
    """Renderiza la sección de información de oficina."""
    st.markdown("### Información de la Oficina")

    oficina_sel = st.selectbox(
        "Selecciona la oficina",
        list(OFICINAS.keys()),
        index=list(OFICINAS.keys()).index(
            var_values.get("Oficina_Seleccionada", "BARCELONA")
        )
    )
    var_values["Oficina_Seleccionada"] = oficina_sel

    sel_data = OFICINAS[oficina_sel]
    for campo in ["Direccion_Oficina", "CP", "Ciudad_Oficina"]:
        if campo not in var_values or var_values[campo] == "":
            var_values[campo] = sel_data[campo]

    edicion_libre = (oficina_sel == "PERSONALIZADA")
    var_values["Direccion_Oficina"] = st.text_input(
        "Dirección de la Oficina",
        value=var_values.get("Direccion_Oficina", ""),
        key="direccion",
        disabled=not edicion_libre
    )
    var_values["CP"] = st.text_input(
        "Código Postal",
        value=var_values.get("CP", ""),
        key="cp",
        disabled=not edicion_libre
    )
    var_values["Ciudad_Oficina"] = st.text_input(
        "Ciudad",
        value=var_values.get("Ciudad_Oficina", ""),
        key="ciudad",
        disabled=not edicion_libre
    )


def render_client_section(var_values: Dict) -> None:
    """Renderiza la sección de nombre de cliente."""
    st.markdown("### Nombre de cliente")
    var_values['Nombre_Cliente'] = st.text_input(
        "Nombre del Cliente",
        value=var_values.get('Nombre_Cliente', ''),
        key="nombre_cliente"
    )


def render_dates_section(var_values: Dict) -> None:
    """Renderiza la sección de fechas."""
    st.markdown("### Fechas")

    fecha_hoy = parse_date_string(var_values.get('Fecha_de_hoy', ''))
    var_values['Fecha_de_hoy'] = st.date_input(
        "Fecha de Hoy",
        value=fecha_hoy
    ).strftime("%d de %B de %Y")

    fecha_encargo = parse_date_string(var_values.get('Fecha_encargo', ''))
    var_values['Fecha_encargo'] = st.date_input(
        "Fecha del Encargo",
        value=fecha_encargo
    ).strftime("%d de %B de %Y")

    fecha_ff = parse_date_string(var_values.get('FF_Ejecicio', ''))
    var_values['FF_Ejecicio'] = st.date_input(
        "Fecha Fin del Ejercicio",
        value=fecha_ff
    ).strftime("%d de %B de %Y")

    fecha_cierre = parse_date_string(var_values.get('Fecha_cierre', ''))
    var_values['Fecha_cierre'] = st.date_input(
        "Fecha de Cierre",
        value=fecha_cierre
    ).strftime("%d de %B de %Y")


def render_general_info_section(var_values: Dict) -> None:
    """Renderiza la sección de información general."""
    st.markdown("### Información General")
    var_values['Lista_Abogados'] = st.text_area(
        "Lista de abogados y asesores fiscales",
        value=var_values.get('Lista_Abogados', ''),
        placeholder="Ej: Despacho ABC - Asesoría fiscal\nDespacho XYZ - Asesoría legal",
        key="abogados"
    )
    var_values['anexo_partes'] = st.text_input(
        "Número anexo partes vinculadas",
        value=var_values.get('anexo_partes', '2')
    )
    var_values['anexo_proyecciones'] = st.text_input(
        "Número anexo proyecciones",
        value=var_values.get('anexo_proyecciones', '3')
    )


def render_organ_section(cond_values: Dict, imported_data: Dict) -> None:
    """Renderiza la sección de órgano de administración."""
    st.markdown("### Órgano de Administración")

    if 'organo' in imported_data:
        organo_default = imported_data['organo']
    else:
        organo_default = cond_values.get('organo', 'consejo')

    cond_values['organo'] = st.selectbox(
        "Tipo de Órgano de Administración",
        options=['consejo', 'administrador_unico', 'administradores'],
        index=['consejo', 'administrador_unico', 'administradores'].index(organo_default),
        format_func=lambda x: {
            'consejo': 'Consejo de Administración',
            'administrador_unico': 'Administrador Único',
            'administradores': 'Administradores'
        }[x]
    )


def render_conditional_options(cond_values: Dict, var_values: Dict) -> None:
    """Renderiza las opciones condicionales."""
    st.markdown("### Opciones Condicionales")

    # Comisión de Auditoría
    cond_values['comision'] = 'sí' if st.checkbox(
        "¿Existe Comisión de Auditoría?",
        value=(cond_values.get('comision', 'no') == 'sí')
    ) else 'no'

    # Junta y Comité
    cond_values['junta'] = 'sí' if st.checkbox(
        "¿Incluir Junta de Accionistas?",
        value=(cond_values.get('junta', 'no') == 'sí')
    ) else 'no'

    cond_values['comite'] = 'sí' if st.checkbox(
        "¿Incluir Comité?",
        value=(cond_values.get('comite', 'no') == 'sí')
    ) else 'no'

    # Incorrecciones
    cond_values['incorreccion'] = 'sí' if st.checkbox(
        "¿Hay incorrecciones no corregidas?",
        value=(cond_values.get('incorreccion', 'no') == 'sí')
    ) else 'no'

    if cond_values['incorreccion'] == 'sí':
        with st.container():
            st.markdown("##### Detalles de incorrecciones")
            var_values['Anio_incorreccion'] = st.text_input(
                "Año de la incorrección",
                value=var_values.get('Anio_incorreccion', ''),
                key="anio_inc"
            )
            var_values['Epigrafe'] = st.text_input(
                "Epígrafe afectado",
                value=var_values.get('Epigrafe', ''),
                key="epigrafe"
            )
            if 'limitacion_alcance' not in cond_values:
                cond_values['limitacion_alcance'] = 'no'
            cond_values['limitacion_alcance'] = 'sí' if st.checkbox(
                "¿Hay limitación al alcance?",
                value=(cond_values.get('limitacion_alcance', 'no') == 'sí')
            ) else 'no'
            if cond_values['limitacion_alcance'] == 'sí':
                var_values['detalle_limitacion'] = st.text_area(
                    "Detalle de la limitación",
                    value=var_values.get('detalle_limitacion', ''),
                    key="det_limitacion"
                )

    # Dudas empresa en funcionamiento
    cond_values['dudas'] = 'sí' if st.checkbox(
        "¿Existen dudas sobre empresa en funcionamiento?",
        value=(cond_values.get('dudas', 'no') == 'sí')
    ) else 'no'

    # Arrendamientos
    cond_values['rent'] = 'sí' if st.checkbox(
        "¿Incluir párrafo sobre arrendamientos?",
        value=(cond_values.get('rent', 'no') == 'sí')
    ) else 'no'

    # Valor razonable a Coste
    cond_values['A_coste'] = 'sí' if st.checkbox(
        "¿Hay activos valorados a coste en vez de valor razonable?",
        value=(cond_values.get('A_coste', 'no') == 'sí')
    ) else 'no'

    # Experto independiente
    cond_values['experto'] = 'sí' if st.checkbox(
        "¿Se utilizó un experto independiente?",
        value=(cond_values.get('experto', 'no') == 'sí')
    ) else 'no'

    if cond_values['experto'] == 'sí':
        with st.container():
            st.markdown("##### Información del experto")
            var_values['nombre_experto'] = st.text_input(
                "Nombre del experto",
                value=var_values.get('nombre_experto', ''),
                key="experto_nombre"
            )
            var_values['experto_valoracion'] = st.text_input(
                "Elemento valorado por experto",
                value=var_values.get('experto_valoracion', ''),
                key="experto_val"
            )

    # Unidad de decisión
    cond_values['unidad_decision'] = 'sí' if st.checkbox(
        "¿Bajo la misma unidad de decisión?",
        value=(cond_values.get('unidad_decision', 'no') == 'sí')
    ) else 'no'

    if cond_values['unidad_decision'] == 'sí':
        with st.container():
            st.markdown("##### Información de la unidad de decisión")
            var_values['nombre_unidad'] = st.text_input(
                "Nombre de la unidad",
                value=var_values.get('nombre_unidad', ''),
                key="nombre_unidad"
            )
            var_values['nombre_mayor_sociedad'] = st.text_input(
                "Nombre de la mayor sociedad",
                value=var_values.get('nombre_mayor_sociedad', ''),
                key="nombre_mayor_sociedad"
            )
            var_values['localizacion_mer'] = st.text_input(
                "Localización o domiciliación mercantil",
                value=var_values.get('localizacion_mer', ''),
                key="localizacion_mer"
            )

    # Activos por impuestos
    cond_values['activo_impuesto'] = 'sí' if st.checkbox(
        "¿Hay activos por impuestos diferidos?",
        value=(cond_values.get('activo_impuesto', 'no') == 'sí')
    ) else 'no'

    if cond_values['activo_impuesto'] == 'sí':
        with st.container():
            st.markdown("##### Recuperación de activos")
            var_values['ejercicio_recuperacion_inicio'] = st.text_input(
                "Ejercicio inicio recuperación",
                value=var_values.get('ejercicio_recuperacion_inicio', ''),
                key="rec_inicio"
            )
            var_values['ejercicio_recuperacion_fin'] = st.text_input(
                "Ejercicio fin recuperación",
                value=var_values.get('ejercicio_recuperacion_fin', ''),
                key="rec_fin"
            )

    # Operaciones en paraísos fiscales
    cond_values['operacion_fiscal'] = 'sí' if st.checkbox(
        "¿Operaciones en paraísos fiscales?",
        value=(cond_values.get('operacion_fiscal', 'no') == 'sí')
    ) else 'no'

    if cond_values['operacion_fiscal'] == 'sí':
        with st.container():
            st.markdown("##### Detalle operaciones")
            var_values['detalle_operacion_fiscal'] = st.text_area(
                "Detalle operaciones paraísos fiscales",
                value=var_values.get('detalle_operacion_fiscal', ''),
                key="det_fiscal"
            )

    # Compromisos por pensiones
    cond_values['compromiso'] = 'sí' if st.checkbox(
        "¿Compromisos por pensiones?",
        value=(cond_values.get('compromiso', 'no') == 'sí')
    ) else 'no'

    # Informe de gestión
    cond_values['gestion'] = 'sí' if st.checkbox(
        "¿Incluir informe de gestión?",
        value=(cond_values.get('gestion', 'no') == 'sí')
    ) else 'no'


def render_directors_section(var_values: Dict) -> List[str]:
    """Renderiza la sección de altos directivos."""
    st.markdown("---")
    st.markdown("### Alta Dirección")

    imported_directivos = var_values.get('lista_alto_directores', '')

    if imported_directivos:
        directivos_lines = imported_directivos.strip().split('\n')
        directivos_list = [line.strip() for line in directivos_lines if line.strip()]

        st.info(f"Se importaron {len(directivos_list)} directivos")
        st.text_area("Directivos importados:", value='\n'.join(directivos_list), height=100, disabled=True)

        use_imported = st.checkbox("Usar directivos importados", value=True)

        if not use_imported:
            st.info("Introduce los nombres y cargos de los altos directivos.")
            num_directivos = st.number_input("Número de altos directivos", min_value=0, max_value=10, value=len(directivos_list))

            directivos_list = []
            indent = "                                  "
            for i in range(num_directivos):
                col_nombre, col_cargo = st.columns(2)
                with col_nombre:
                    nombre = st.text_input(f"Nombre completo {i+1}", key=f"dir_nombre_{i}")
                with col_cargo:
                    cargo = st.text_input(f"Cargo {i+1}", key=f"dir_cargo_{i}")
                if nombre and cargo:
                    directivos_list.append(f"{indent} D. {nombre} - {cargo}")
    else:
        st.info("Introduce los nombres y cargos de los altos directivos. Estos reemplazarán completamente el ejemplo en la plantilla.")

        num_directivos = st.number_input("Número de altos directivos", min_value=0, max_value=10, value=2)

        directivos_list = []
        indent = "                                  "
        for i in range(num_directivos):
            col_nombre, col_cargo = st.columns(2)
            with col_nombre:
                nombre = st.text_input(f"Nombre completo {i+1}", key=f"dir_nombre_{i}")
            with col_cargo:
                cargo = st.text_input(f"Cargo {i+1}", key=f"dir_cargo_{i}")
            if nombre and cargo:
                directivos_list.append(f"{indent} D. {nombre} - {cargo}")

    return directivos_list


def render_signature_section(var_values: Dict) -> None:
    """Renderiza la sección de persona de firma."""
    st.markdown("---")
    st.markdown("### Persona de firma")
    var_values['Nombre_Firma'] = st.text_input(
        "Nombre del firmante",
        value=var_values.get('Nombre_Firma', ''),
        key="nombre_firma"
    )
    var_values['Cargo_Firma'] = st.text_input(
        "Cargo del firmante",
        value=var_values.get('Cargo_Firma', ''),
        key="cargo_firma"
    )


def render_review_section(
    required_vars: List[str],
    var_values: Dict,
    cond_values: Dict,
    imported_data: Dict,
    variables: List[str],
    conditionals: List[str]
) -> None:
    """Renderiza la sección de revisión automática."""
    st.markdown("---")
    st.header("Revisión automática")

    missing_vars = [v for v in required_vars if v not in var_values or var_values[v] == ""]
    missing_conds = [c for c in conditionals if c not in cond_values]

    if imported_data:
        st.info(f"Datos importados: {len([k for k in imported_data if k in var_values])} variables y {len([k for k in imported_data if k in cond_values])} condiciones")

    if not missing_vars and not missing_conds:
        st.success("Todas las variables y condiciones están completas.")
    else:
        st.warning(f"Faltan {len(missing_vars)} variables y {len(missing_conds)} condiciones.")

        with st.expander("Ver / completar elementos faltantes"):
            for var in missing_vars:
                var_values[var] = st.text_input(f"Valor para «{var}»", key=f"auto_{var}")

            for cond in missing_conds:
                cond_values[cond] = 'sí' if st.checkbox(f"Activar condición «{cond}»", key=f"auto_{cond}") else 'no'


def main():
    """Función principal de la aplicación."""
    # Inicializar servicio
    service = CartaManifestacionService()

    # Enviar evento de apertura de la app
    service.send_telemetry_event("open", {"timestamp": datetime.now().isoformat()})

    # Verificar plantilla
    exists, error = service.verify_template_exists()
    if not exists:
        st.error(f"⚠️ {error}")
        st.info("Por favor, asegúrate de que el archivo de plantilla esté en la carpeta de la aplicación.")
        return

    # Extraer variables y condicionales
    with st.spinner("Analizando plantilla..."):
        variables, conditionals = service.extract_variables_from_template()

    st.success(f"Plantilla analizada. Se encontraron {len(variables)} variables y {len(conditionals)} condicionales.")

    # Sección de importación
    st.markdown("---")
    st.subheader("Importar datos desde archivo")

    col_import1, col_import2 = st.columns(2)

    var_values = {}
    cond_values = {}
    imported_data = {}

    with col_import1:
        uploaded_excel = st.file_uploader(
            "Cargar archivo Excel (.xlsx, .xls)",
            type=['xlsx', 'xls'],
            help="Formato: Columna 1 = Nombre variable, Columna 2 = Valor"
        )

    with col_import2:
        uploaded_word = st.file_uploader(
            "Cargar archivo Word (.docx)",
            type=['docx'],
            help="Formato: nombre_variable: valor (una por línea)"
        )

    if uploaded_excel is not None:
        with st.spinner("Procesando archivo Excel..."):
            try:
                var_values, cond_values = service.process_uploaded_file(
                    uploaded_excel, "excel", variables, conditionals
                )
                imported_data = {**var_values, **cond_values}
                st.success(f"Se importaron {len(imported_data)} valores desde Excel")
            except Exception as e:
                st.error(f"Error al procesar Excel: {str(e)}")

    elif uploaded_word is not None:
        with st.spinner("Procesando archivo Word..."):
            try:
                var_values, cond_values = service.process_uploaded_file(
                    uploaded_word, "word", variables, conditionals
                )
                imported_data = {**var_values, **cond_values}
                st.success(f"Se importaron {len(imported_data)} valores desde Word")
            except Exception as e:
                st.error(f"Error al procesar Word: {str(e)}")

    st.markdown("---")

    # Formulario principal
    st.subheader("Información de la Carta")

    col1, col2 = st.columns(2)

    with col1:
        render_office_section(var_values, imported_data)
        render_client_section(var_values)
        render_dates_section(var_values)
        render_general_info_section(var_values)

    with col2:
        render_organ_section(cond_values, imported_data)
        render_conditional_options(cond_values, var_values)

    # Directivos
    directivos_list = render_directors_section(var_values)
    var_values['lista_alto_directores'] = "\n".join(directivos_list)

    if directivos_list:
        st.markdown("#### Vista previa de la lista de directivos:")
        st.code("\n".join(directivos_list))

    # Firma
    render_signature_section(var_values)

    # Revisión
    required_vars = service.calculate_required_variables(variables, cond_values)
    render_review_section(
        required_vars, var_values, cond_values,
        imported_data, variables, conditionals
    )

    # Botón de generación
    st.markdown("---")

    if st.button("Generar Carta de Manifestación", type="primary"):
        with st.spinner("Generando carta..."):
            success, doc_buffer, filename, error = service.generate_document(
                var_values, cond_values, variables
            )

            if success:
                st.success("Carta generada exitosamente!")

                # Enviar evento de telemetría
                service.send_telemetry_event("generate_document", {
                    "client": var_values.get('Nombre_Cliente', ''),
                    "timestamp": datetime.now().isoformat()
                })

                # Botón de descarga
                st.download_button(
                    label="Descargar Carta de Manifestación",
                    data=doc_buffer,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            else:
                st.error(f"❌ {error}")
                service.send_telemetry_event("error", {"error": error})


if __name__ == "__main__":
    main()
