"""
Procesadores de Archivos - App Carta Manifestación
==================================================

Funciones para procesar archivos Excel y Word y extraer variables.
"""

from typing import Dict, BinaryIO
from datetime import datetime
import pandas as pd
from docx import Document

from .constants import VARIABLE_NAME_MAPPING


def normalize_value(value: str) -> str:
    """
    Normaliza valores de variables (convierte SI/NO a sí/no).

    Args:
        value: Valor a normalizar

    Returns:
        str: Valor normalizado
    """
    if value.upper() in ['SI', 'SÍ'] or value == '1':
        return 'sí'
    elif value.upper() == 'NO' or value == '0':
        return 'no'
    return value


def normalize_variable_name(var_name: str) -> str:
    """
    Normaliza el nombre de una variable usando el mapeo.

    Args:
        var_name: Nombre de variable

    Returns:
        str: Nombre normalizado
    """
    normalized = var_name.lower().replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')

    if normalized in VARIABLE_NAME_MAPPING:
        return VARIABLE_NAME_MAPPING[normalized]

    return var_name


def process_excel_file(file: BinaryIO) -> Dict[str, str]:
    """
    Procesa archivo Excel y extrae variables y sus valores.

    Args:
        file: Archivo Excel

    Returns:
        Dict: Diccionario con variables y valores
    """
    extracted_data = {}

    try:
        # Leer Excel con pandas
        df = pd.read_excel(file, header=None)

        # Verificar que tenga al menos 2 columnas
        if df.shape[1] >= 2:
            # Iterar por las filas
            for index, row in df.iterrows():
                if pd.notna(row[0]) and pd.notna(row[1]):
                    var_name = str(row[0]).strip()
                    var_value = row[1]

                    # Si es una fecha/datetime, convertirla a string
                    if pd.api.types.is_datetime64_any_dtype(type(var_value)) or isinstance(var_value, datetime):
                        var_value = var_value.strftime("%d/%m/%Y")
                    else:
                        var_value = str(var_value).strip()

                    # Normalizar valor
                    var_value = normalize_value(var_value)

                    # Normalizar nombre de variable
                    var_name = normalize_variable_name(var_name)

                    extracted_data[var_name] = var_value

    except Exception as e:
        raise Exception(f"Error al procesar archivo Excel: {str(e)}")

    return extracted_data


def process_word_file(file: BinaryIO) -> Dict[str, str]:
    """
    Procesa archivo Word y extrae variables y sus valores.

    Args:
        file: Archivo Word

    Returns:
        Dict: Diccionario con variables y valores
    """
    extracted_data = {}

    try:
        # Leer documento Word
        doc = Document(file)

        # Extraer texto de todos los párrafos
        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if text and ':' in text:
                # Dividir por el primer ':' encontrado
                parts = text.split(':', 1)
                if len(parts) == 2:
                    var_name = parts[0].strip()
                    var_value = parts[1].strip()

                    # Normalizar valor
                    var_value = normalize_value(var_value)

                    # Normalizar nombre de variable
                    var_name = normalize_variable_name(var_name)

                    extracted_data[var_name] = var_value

    except Exception as e:
        raise Exception(f"Error al procesar archivo Word: {str(e)}")

    return extracted_data
