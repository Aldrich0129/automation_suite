"""
Constantes y configuraciones - App Carta Manifestación
======================================================

Define constantes de negocio como oficinas, configuraciones, etc.
"""

OFICINAS = {
    "ALICANTE": {
        "Direccion_Oficina": "Pintor Cabrera 22, esc. B, planta 4 A",
        "CP": "03003",
        "Ciudad_Oficina": "Alicante"
    },
    "BARCELONA": {
        "Direccion_Oficina": "C/ Diputació, 260",
        "CP": "08007",
        "Ciudad_Oficina": "Barcelona"
    },
    "BILBAO": {
        "Direccion_Oficina": "C/ Rodríguez Arias, 23, planta 6ª, Dpto. 12",
        "CP": "48011",
        "Ciudad_Oficina": "Bilbao"
    },
    "MADRID (Alcalá 63)": {
        "Direccion_Oficina": "C/ Alcalá, 63",
        "CP": "28014",
        "Ciudad_Oficina": "Madrid"
    },
    "MADRID (Alcalá 61-3ª)": {
        "Direccion_Oficina": "C/ Alcalá, 61, Planta 3ª",
        "CP": "28014",
        "Ciudad_Oficina": "Madrid"
    },
    "MÁLAGA": {
        "Direccion_Oficina": "Pirandello nº 6 portal 3, planta 6ª, puerta 4ª",
        "CP": "29010",
        "Ciudad_Oficina": "Málaga"
    },
    "VALENCIA": {
        "Direccion_Oficina": "C/ Félix Pizcueta, 4 – 4º",
        "CP": "46004",
        "Ciudad_Oficina": "Valencia"
    },
    "VIGO": {
        "Direccion_Oficina": "C/ República Argentina, 25 – 1º Izda",
        "CP": "36201",
        "Ciudad_Oficina": "Vigo"
    },
    "PERSONALIZADA": {
        "Direccion_Oficina": "",
        "CP": "",
        "Ciudad_Oficina": ""
    }
}

# Mapeo de nombres alternativos para normalización
VARIABLE_NAME_MAPPING = {
    'comision': 'comision',
    'comisión': 'comision',
    'organo': 'organo',
    'órgano': 'organo'
}

# Campos obligatorios para generar carta
REQUIRED_FIELDS = ['Nombre_Cliente', 'Direccion_Oficina', 'CP', 'Ciudad_Oficina']

# Mapeo de variables condicionales
CONDITIONAL_VARS_MAP = {
    'incorreccion': ['Anio_incorreccion', 'Epigrafe', 'detalle_limitacion'],
    'experto': ['nombre_experto', 'experto_valoracion'],
    'activo_impuesto': ['ejercicio_recuperacion_inicio', 'ejercicio_recuperacion_fin'],
    'operacion_fiscal': ['detalle_operacion_fiscal'],
    'unidad_decision': ['nombre_unidad', 'nombre_mayor_sociedad', 'localizacion_mer']
}
