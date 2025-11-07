# Generador de Cartas de Manifestación

Aplicación modular para generar cartas de manifestación de auditoría a partir de plantillas Word.

## Arquitectura

Esta aplicación sigue la arquitectura estándar **UI → Services → Domain**:

```
apps/app_carta_manifestacion/
├── app/
│   ├── domain/              # Lógica pura de negocio
│   │   ├── constants.py     # Constantes (oficinas, mapeos)
│   │   ├── date_utils.py    # Utilidades de fechas
│   │   ├── file_parsers.py  # Procesadores Excel/Word
│   │   └── document_processor.py  # Generador de cartas
│   ├── services.py          # Orquestación y servicios
│   └── ui.py                # Interfaz Streamlit
├── .streamlit/
│   └── config.toml          # Configuración Streamlit
├── requirements.txt         # Dependencias
├── run_local.sh            # Script de ejecución local
├── register_app.py         # Script de registro en backend
└── README.md               # Este archivo
```

## Requisitos

- Python 3.10+
- Archivo de plantilla: `Modelo de plantilla.docx` (debe estar en la raíz de la app)

## Instalación

1. Instalar dependencias:

```bash
cd apps/app_carta_manifestacion
pip install -r requirements.txt
```

2. Colocar el archivo de plantilla:

```bash
# Copiar Modelo de plantilla.docx a apps/app_carta_manifestacion/
cp /ruta/a/Modelo\ de\ plantilla.docx apps/app_carta_manifestacion/
```

## Ejecución Local

### Método 1: Script automático

```bash
cd apps/app_carta_manifestacion
./run_local.sh
```

La aplicación estará disponible en: http://localhost:8602/app_carta_manifestacion

### Método 2: Comando Streamlit directo

```bash
cd apps/app_carta_manifestacion
streamlit run app/ui.py \
  --server.port=8602 \
  --server.baseUrlPath=/app_carta_manifestacion
```

## Integración con el Portal

### 1. Registrar la app en el backend

```bash
cd apps/app_carta_manifestacion
python register_app.py
```

Este script registra la aplicación en el catálogo del backend con:
- **ID**: `app_carta_manifestacion`
- **Nombre**: Generador de Carta de Manifestación
- **Ruta**: `/app_carta_manifestacion`
- **Tags**: Auditoría, Documentos
- **Modo de acceso**: Público

### 2. Verificar en el portal

Accede al portal en http://localhost:8600/portal y verifica que la app aparezca en el catálogo.

## Funcionalidades

### Generación de Cartas

1. **Importación de datos**: Soporta archivos Excel y Word
2. **Formulario interactivo**: Campos organizados por secciones
3. **Validación automática**: Verifica campos obligatorios
4. **Generación de documento**: Procesa plantilla y genera carta final

### Telemetría

La aplicación envía eventos de telemetría al backend:

- `open`: Al iniciar la aplicación
- `generate_document`: Al generar una carta
- `error`: En caso de errores

Los eventos se pueden visualizar en el panel de administración del portal.

### Variables soportadas

La aplicación extrae automáticamente todas las variables de la plantilla Word, incluyendo:

- Información de oficina (dirección, CP, ciudad)
- Datos del cliente
- Fechas (hoy, encargo, cierre, ejercicio)
- Condiciones (auditoría, comisión, expertos, etc.)
- Lista de altos directivos
- Información del firmante

## Desarrollo

### Añadir nuevas funcionalidades

1. **Lógica de negocio**: Modificar archivos en `app/domain/`
2. **Servicios**: Modificar `app/services.py`
3. **Interfaz**: Modificar `app/ui.py`

### Ejecutar en modo desarrollo

```bash
# Con recarga automática
streamlit run app/ui.py --server.runOnSave=true
```

## Solución de problemas

### La plantilla no se encuentra

Asegúrate de que `Modelo de plantilla.docx` esté en:
```
apps/app_carta_manifestacion/Modelo de plantilla.docx
```

### Error de conexión con el backend

Verifica que:
1. El backend esté ejecutándose en http://localhost:8601
2. La variable de entorno `BACKEND_BASE_URL` esté configurada correctamente

### Eventos de telemetría no aparecen

La telemetría falla silenciosamente si el backend no está disponible. Esto es intencional para que la app funcione de forma standalone.

## Licencia

© Forvis Mazars - Automation Suite
