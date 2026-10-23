-- ============================================================
-- Sesión 11 | Databricks: S3 y Genie Agents
-- Tatiana Conde — Proyecto IPD (Instituto Peruano del Deporte)
-- 5 Consultas SQL sobre: ggrrr.s11_ipd.deportistas_s3
-- Archivo fuente: ipd_deportistas_real.csv (50 registros)
-- EJECUTAR EN: SQL Editor de Databricks
-- ============================================================

USE CATALOG ggrrr;
USE SCHEMA s11_ipd;

-- ============================================================
-- CONSULTA 1: Medallero por federación
-- ¿Cuántos oros, platas y bronces tiene cada federación?
-- ============================================================
SELECT
  federacion,
  COUNT(*)                                          AS total_participaciones,
  SUM(CASE WHEN puesto = 1 THEN 1 ELSE 0 END)      AS oros,
  SUM(CASE WHEN puesto = 2 THEN 1 ELSE 0 END)      AS platas,
  SUM(CASE WHEN puesto = 3 THEN 1 ELSE 0 END)      AS bronces,
  ROUND(AVG(monto_pad), 2)                          AS promedio_pad
FROM ggrrr.s11_ipd.deportistas_s3
GROUP BY federacion
ORDER BY oros DESC, platas DESC;

-- ============================================================
-- CONSULTA 2: Top deportistas con mayor apoyo PAD
-- ¿Qué deportistas recibieron más apoyo económico PAD?
-- ============================================================
SELECT
  deportista,
  federacion,
  departamento,
  SUM(monto_pad)   AS total_pad,
  COUNT(*)         AS eventos_participados,
  MIN(puesto)      AS mejor_puesto
FROM ggrrr.s11_ipd.deportistas_s3
GROUP BY deportista, federacion, departamento
ORDER BY total_pad DESC
LIMIT 10;

-- ============================================================
-- CONSULTA 3: Participaciones internacionales por departamento
-- ¿Qué departamento tiene más deportistas en eventos internacionales?
-- ============================================================
SELECT
  departamento,
  COUNT(DISTINCT deportista)   AS deportistas_unicos,
  COUNT(*)                     AS total_participaciones,
  ROUND(SUM(monto_pad), 2)     AS inversion_pad_total,
  ROUND(AVG(puesto), 1)        AS puesto_promedio
FROM ggrrr.s11_ipd.deportistas_s3
GROUP BY departamento
ORDER BY deportistas_unicos DESC;

-- ============================================================
-- CONSULTA 4: Eventos con mayor participación peruana
-- ¿En qué eventos internacionales participaron más deportistas peruanos?
-- ============================================================
SELECT
  evento,
  pais_evento,
  COUNT(DISTINCT deportista)  AS deportistas,
  COUNT(DISTINCT federacion)  AS federaciones,
  MIN(puesto)                 AS mejor_puesto,
  ROUND(SUM(monto_pad), 2)    AS inversion_total
FROM ggrrr.s11_ipd.deportistas_s3
GROUP BY evento, pais_evento
ORDER BY deportistas DESC;

-- ============================================================
-- CONSULTA 5: Ranking de deportistas por año (Window Function)
-- Ranking según puesto y monto PAD por año
-- ============================================================
SELECT
  anio,
  deportista,
  federacion,
  evento,
  puesto,
  monto_pad,
  RANK() OVER (
    PARTITION BY anio
    ORDER BY puesto ASC, monto_pad DESC
  ) AS ranking_anio
FROM ggrrr.s11_ipd.deportistas_s3
ORDER BY anio DESC, ranking_anio;
