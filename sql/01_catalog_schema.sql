-- ============================================================
-- Sesión 11 | Databricks: S3 y Genie Agents
-- Tatiana Conde
-- Estructura: catalog.schema.tabla
-- EJECUTAR EN: SQL Editor de Databricks (menú izquierdo)
-- ============================================================

-- 1. Crear el Schema dentro del catalog ggrrr
CREATE SCHEMA IF NOT EXISTS ggrrr.s11_ventas
  COMMENT 'Schema S11 - Tatiana Conde - Ventas desde S3';

-- 2. Crear la tabla Delta (Golden layer desde S3)
CREATE TABLE IF NOT EXISTS ggrrr.s11_ventas.productos_s3 (
  id        INT     COMMENT 'ID del producto',
  producto  STRING  COMMENT 'Nombre del producto',
  precio    DOUBLE  COMMENT 'Precio unitario en USD',
  categoria STRING  COMMENT 'Categoria del producto',
  cantidad  INT     COMMENT 'Cantidad vendida',
  ciudad    STRING  COMMENT 'Ciudad de venta',
  fecha     DATE    COMMENT 'Fecha de la venta'
)
USING DELTA
COMMENT 'Tabla productos cargada desde Amazon S3 - Golden layer';

-- 3. Verificar
SHOW TABLES IN ggrrr.s11_ventas;
