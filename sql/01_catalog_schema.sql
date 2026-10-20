-- ============================================================
-- Sesión 11 | Databricks: S3 y Genie Agents
-- Tatiana Conde — Proyecto IPD (Instituto Peruano del Deporte)
-- Estructura: ggrrr.s11_ipd.deportistas_s3
-- EJECUTAR EN: SQL Editor de Databricks
-- ============================================================

-- 1. Crear el Schema dentro del catalog ggrrr
CREATE SCHEMA IF NOT EXISTS ggrrr.s11_ipd
  COMMENT 'Schema S11 - IPD Deportistas desde S3';

-- 2. Crear la tabla Delta (Golden layer desde S3)
CREATE TABLE IF NOT EXISTS ggrrr.s11_ipd.deportistas_s3 (
  federacion    STRING  COMMENT 'Federacion deportiva',
  deportista    STRING  COMMENT 'Nombre del deportista',
  evento        STRING  COMMENT 'Nombre del evento internacional',
  pais_evento   STRING  COMMENT 'Pais donde se realizo el evento',
  especialidad  STRING  COMMENT 'Especialidad o prueba deportiva',
  puesto        INT     COMMENT 'Puesto obtenido en el evento',
  departamento  STRING  COMMENT 'Departamento de origen del deportista',
  anio          INT     COMMENT 'Anio de participacion',
  monto_pad     DOUBLE  COMMENT 'Monto de apoyo PAD en soles'
)
USING DELTA
COMMENT 'Deportistas IPD cargados desde Amazon S3 - Golden layer';

-- 3. Verificar
SHOW TABLES IN ggrrr.s11_ipd;
