-- Script SQL para registrar la app en el backend
-- ================================================

INSERT INTO apps (
    id,
    name,
    description,
    path,
    tags,
    enabled,
    access_mode,
    created_at,
    updated_at
) VALUES (
    'app_carta_manifestacion',
    'Generador de Carta de Manifestación',
    'Herramienta para generar cartas de manifestación de auditoría a partir de plantillas Word.',
    '/app_carta_manifestacion',
    'Auditoría,Documentos',
    true,
    'public',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    path = EXCLUDED.path,
    tags = EXCLUDED.tags,
    enabled = EXCLUDED.enabled,
    access_mode = EXCLUDED.access_mode,
    updated_at = CURRENT_TIMESTAMP;
