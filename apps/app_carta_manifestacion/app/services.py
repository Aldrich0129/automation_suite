"""
Services - App Carta Manifestación
===================================

Capa de servicios y orquestación de lógica de negocio.
Integra con backend para telemetría y validaciones.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional, BinaryIO, Tuple, List
from datetime import datetime
import io
import requests

from domain import (
    CartaManifestacionGenerator,
    process_excel_file,
    process_word_file,
    REQUIRED_FIELDS,
    CONDITIONAL_VARS_MAP,
    OFICINAS,
    set_spanish_locale
)

# Añadir el directorio core al path
CORE_PATH = Path(__file__).parent.parent.parent.parent / "core"
sys.path.insert(0, str(CORE_PATH))

try:
    from core.settings import get_backend_base_url
except ImportError:
    def get_backend_base_url():
        return os.getenv("BACKEND_BASE_URL", "http://localhost:8000")


class CartaManifestacionService:
    """Servicio principal para la generación de cartas de manifestación."""

    def __init__(self, template_path: str = "Modelo de plantilla.docx"):
        """
        Inicializa el servicio.

        Args:
            template_path: Ruta a la plantilla Word
        """
        self.template_path = template_path
        self.backend_url = get_backend_base_url()
        set_spanish_locale()

    def verify_template_exists(self) -> Tuple[bool, Optional[str]]:
        """
        Verifica que la plantilla existe.

        Returns:
            Tuple: (existe, mensaje de error si aplica)
        """
        if not os.path.exists(self.template_path):
            return False, f"No se encontró el archivo '{self.template_path}'"
        return True, None

    def extract_variables_from_template(self) -> Tuple[List[str], List[str]]:
        """
        Extrae variables y condicionales de la plantilla.

        Returns:
            Tuple: (lista de variables, lista de condicionales)
        """
        generator = CartaManifestacionGenerator(self.template_path)
        return generator.extract_variables()

    def process_uploaded_file(
        self,
        file: BinaryIO,
        file_type: str,
        variables: List[str],
        conditionals: List[str]
    ) -> Tuple[Dict[str, str], Dict[str, str]]:
        """
        Procesa un archivo Excel o Word cargado y separa variables y condiciones.

        Args:
            file: Archivo subido
            file_type: 'excel' o 'word'
            variables: Lista de variables esperadas
            conditionals: Lista de condicionales esperadas

        Returns:
            Tuple: (var_values, cond_values)
        """
        if file_type == "excel":
            imported_data = process_excel_file(file)
        elif file_type == "word":
            imported_data = process_word_file(file)
        else:
            raise ValueError(f"Tipo de archivo no soportado: {file_type}")

        # Separar variables y condiciones
        var_values = {}
        cond_values = {}

        for key, value in imported_data.items():
            if key in conditionals:
                cond_values[key] = value
            else:
                var_values[key] = value

        return var_values, cond_values

    def generate_document(
        self,
        var_values: Dict[str, str],
        cond_values: Dict[str, str],
        all_variables: List[str]
    ) -> Tuple[bool, Optional[io.BytesIO], Optional[str], Optional[str]]:
        """
        Genera el documento Word procesado.

        Args:
            var_values: Valores de variables
            cond_values: Valores de condiciones
            all_variables: Lista de todas las variables

        Returns:
            Tuple: (éxito, buffer del documento, nombre archivo, mensaje de error)
        """
        # Validar campos obligatorios
        missing_fields = [field for field in REQUIRED_FIELDS if not var_values.get(field)]

        if missing_fields:
            error_msg = f"Por favor completa los siguientes campos obligatorios: {', '.join(missing_fields)}"
            return False, None, None, error_msg

        try:
            # Asegurar que todas las variables tengan un valor
            for var in all_variables:
                if var not in var_values:
                    var_values[var] = ""

            # Combinar variables y condiciones
            all_vars = {**var_values, **cond_values}

            # Procesar plantilla
            generator = CartaManifestacionGenerator(self.template_path)
            new_doc = generator.process_template(all_vars, cond_values)

            # Guardar en memoria
            doc_buffer = io.BytesIO()
            new_doc.save(doc_buffer)
            doc_buffer.seek(0)

            # Generar nombre de archivo
            filename = f"Carta_Manifestacion_{var_values['Nombre_Cliente'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.docx"

            return True, doc_buffer, filename, None

        except Exception as e:
            return False, None, None, f"Error al generar la carta: {str(e)}"

    def calculate_required_variables(
        self,
        all_variables: List[str],
        cond_values: Dict[str, str]
    ) -> List[str]:
        """
        Calcula las variables requeridas según condiciones activas.

        Args:
            all_variables: Lista de todas las variables
            cond_values: Valores de condiciones

        Returns:
            List: Variables requeridas
        """
        required_vars = set(all_variables)

        for cond, vlist in CONDITIONAL_VARS_MAP.items():
            if cond_values.get(cond, 'no') == 'no':
                required_vars -= set(vlist)

        return list(required_vars)

    def send_telemetry_event(
        self,
        event_type: str,
        meta: Optional[Dict] = None
    ) -> None:
        """
        Envía evento de telemetría al backend.

        Args:
            event_type: Tipo de evento (open, generate_document, error)
            meta: Metadata adicional
        """
        try:
            url = f"{self.backend_url}/api/telemetry"
            payload = {
                "app_id": "app_carta_manifestacion",
                "event_type": event_type,
                "meta": meta or {}
            }

            requests.post(url, json=payload, timeout=5)
        except Exception:
            # Silenciosamente fallar si no hay backend disponible
            pass

    def get_office_data(self, office_name: str) -> Dict[str, str]:
        """
        Obtiene los datos de una oficina.

        Args:
            office_name: Nombre de la oficina

        Returns:
            Dict: Datos de la oficina
        """
        return OFICINAS.get(office_name, OFICINAS["PERSONALIZADA"])

    def validate_access(self, password: Optional[str] = None) -> bool:
        """
        Valida el acceso a la aplicación.
        Punto único para implementar control de acceso futuro.

        Args:
            password: Contraseña si aplica

        Returns:
            bool: True si el acceso es válido
        """
        # Por ahora la app es pública, pero este método permite
        # implementar validación futura sin cambiar la UI
        return True
