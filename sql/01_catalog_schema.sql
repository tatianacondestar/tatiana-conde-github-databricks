-- ============================================================
-- Sesión 11 | Databricks: S3 y Genie Agents
-- Tatiana Conde
-- Creación de Schema y Tabla conectada a S3
-- Catalog usado: ggrrr (existente en el workspace)
-- ============================================================

-- ────────────────────────────────────────────
-- 1. Usar el Catalog existente
-- ────────────────────────────────────────────
USE CATALOG ggrrr;

-- ────────────────────────────────────────────
-- 2. Crear el Schema (base de datos)
-- ────────────────────────────────────────────
CREATE SCHEMA IF NOT EXISTS ggrrr.s11_ventas
  COMMENT 'Schema para datos de ventas - Sesión 11';

-- Usar el schema
USE SCHEMA ggrrr.s11_ventas;

-- ────────────────────────────────────────────
-- 3. Crear tabla Delta en el schema
--    (los datos vendrán de S3 vía el notebook Python)
-- ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ggrrr.s11_ventas.productos_s3 (
  id          INT        COMMENT 'Identificador único del producto',
  producto    STRING     COMMENT 'Nombre del producto',
  precio      DOUBLE     COMMENT 'Precio unitario en USD',
  categoria   STRING     COMMENT 'Categoría del producto',
  cantidad    INT        COMMENT 'Cantidad vendida',
  ciudad      STRING     COMMENT 'Ciudad de venta',
  fecha       DATE       COMMENT 'Fecha de la venta'
)
USING DELTA
COMMENT 'Tabla de productos cargados desde Amazon S3 (Golden/Silver)';

-- Verificar que la tabla existe
DESCRIBE TABLE EXTENDED ggrrr.s11_ventas.productos_s3;

-- ────────────────────────────────────────────
-- 4. Verificar estructura creada
-- ────────────────────────────────────────────
SHOW SCHEMAS IN ggrrr;
SHOW TABLES IN ggrrr.s11_ventas;
