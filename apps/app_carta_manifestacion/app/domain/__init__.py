"""
Domain - App Carta Manifestación
================================

Lógica pura de negocio sin dependencias externas.
"""

from .constants import (
    OFICINAS,
    VARIABLE_NAME_MAPPING,
    REQUIRED_FIELDS,
    CONDITIONAL_VARS_MAP
)
from .date_utils import (
    set_spanish_locale,
    parse_date_string,
    format_date_spanish
)
from .file_parsers import (
    process_excel_file,
    process_word_file,
    normalize_value,
    normalize_variable_name
)
from .document_processor import CartaManifestacionGenerator

__all__ = [
    'OFICINAS',
    'VARIABLE_NAME_MAPPING',
    'REQUIRED_FIELDS',
    'CONDITIONAL_VARS_MAP',
    'set_spanish_locale',
    'parse_date_string',
    'format_date_spanish',
    'process_excel_file',
    'process_word_file',
    'normalize_value',
    'normalize_variable_name',
    'CartaManifestacionGenerator'
]
