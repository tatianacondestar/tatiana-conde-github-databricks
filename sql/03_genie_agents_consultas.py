# Databricks notebook source
# MAGIC %md
# MAGIC # S11 — IPD: 5 Consultas con Genie Agents (AI)
# MAGIC **Sesión 11 | Databricks: S3 y Genie Agents**
# MAGIC Tatiana Conde — Proyecto IPD
# MAGIC
# MAGIC Tabla: `ggrrr.s11_ipd.deportistas_s3`
# MAGIC Archivo fuente: `ipd_deportistas_real.csv` (50 registros)

# COMMAND ----------

# MAGIC %sql
# MAGIC USE CATALOG ggrrr;
# MAGIC USE SCHEMA s11_ipd;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Consulta 1 — Medallero por federación
# MAGIC *Pregunta a Genie: "¿Cuántos puestos 1, 2 y 3 tiene cada federación?"*

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   federacion,
# MAGIC   COUNT(*)                                          AS total_participaciones,
# MAGIC   SUM(CASE WHEN puesto = 1 THEN 1 ELSE 0 END)      AS oros,
# MAGIC   SUM(CASE WHEN puesto = 2 THEN 1 ELSE 0 END)      AS platas,
# MAGIC   SUM(CASE WHEN puesto = 3 THEN 1 ELSE 0 END)      AS bronces,
# MAGIC   ROUND(AVG(monto_pad), 2)                          AS promedio_pad
# MAGIC FROM ggrrr.s11_ipd.deportistas_s3
# MAGIC GROUP BY federacion
# MAGIC ORDER BY oros DESC, platas DESC;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Consulta 2 — Top deportistas con mayor apoyo PAD
# MAGIC *Pregunta a Genie: "¿Qué deportistas recibieron más apoyo económico PAD?"*

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   deportista,
# MAGIC   federacion,
# MAGIC   departamento,
# MAGIC   SUM(monto_pad)   AS total_pad,
# MAGIC   COUNT(*)         AS eventos_participados,
# MAGIC   MIN(puesto)      AS mejor_puesto
# MAGIC FROM ggrrr.s11_ipd.deportistas_s3
# MAGIC GROUP BY deportista, federacion, departamento
# MAGIC ORDER BY total_pad DESC
# MAGIC LIMIT 10;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Consulta 3 — Participaciones internacionales por departamento
# MAGIC *Pregunta a Genie: "¿Qué departamento tiene más deportistas en eventos internacionales?"*

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   departamento,
# MAGIC   COUNT(DISTINCT deportista)   AS deportistas_unicos,
# MAGIC   COUNT(*)                     AS total_participaciones,
# MAGIC   ROUND(SUM(monto_pad), 2)     AS inversion_pad_total,
# MAGIC   ROUND(AVG(puesto), 1)        AS puesto_promedio
# MAGIC FROM ggrrr.s11_ipd.deportistas_s3
# MAGIC GROUP BY departamento
# MAGIC ORDER BY deportistas_unicos DESC;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Consulta 4 — Eventos con mayor participación peruana
# MAGIC *Pregunta a Genie: "¿En qué eventos internacionales participaron más deportistas peruanos?"*

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   evento,
# MAGIC   pais_evento,
# MAGIC   COUNT(DISTINCT deportista)  AS deportistas,
# MAGIC   COUNT(DISTINCT federacion)  AS federaciones,
# MAGIC   MIN(puesto)                 AS mejor_puesto,
# MAGIC   ROUND(SUM(monto_pad), 2)    AS inversion_total
# MAGIC FROM ggrrr.s11_ipd.deportistas_s3
# MAGIC GROUP BY evento, pais_evento
# MAGIC ORDER BY deportistas DESC;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Consulta 5 — Ranking de deportistas por anio con Window Function
# MAGIC *Pregunta a Genie: "Muéstrame el ranking de deportistas por año según su puesto"*

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   anio,
# MAGIC   deportista,
# MAGIC   federacion,
# MAGIC   evento,
# MAGIC   puesto,
# MAGIC   monto_pad,
# MAGIC   RANK() OVER (
# MAGIC     PARTITION BY anio
# MAGIC     ORDER BY puesto ASC, monto_pad DESC
# MAGIC   ) AS ranking_anio
# MAGIC FROM ggrrr.s11_ipd.deportistas_s3
# MAGIC ORDER BY anio DESC, ranking_anio;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Resumen — Consultas Genie Agents IPD
# MAGIC | # | Pregunta | Técnica SQL |
# MAGIC |---|---|---|
# MAGIC | 1 | Medallero por federación | CASE WHEN + GROUP BY |
# MAGIC | 2 | Top deportistas PAD | SUM + GROUP BY |
# MAGIC | 3 | Participaciones por departamento | COUNT DISTINCT |
# MAGIC | 4 | Eventos con más peruanos | GROUP BY múltiple |
# MAGIC | 5 | Ranking por año | Window RANK() |
