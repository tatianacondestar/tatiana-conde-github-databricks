# Databricks notebook source
# MAGIC %md
# MAGIC # S11 — 5 Consultas con Genie Agents (AI)
# MAGIC **Sesión 11 | Databricks: S3 y Genie Agents**
# MAGIC Tatiana Conde
# MAGIC
# MAGIC Tabla fuente: `ggrrr.s11_ventas.productos_s3`
# MAGIC
# MAGIC Consultas generadas con Databricks Genie AI

# COMMAND ----------

# MAGIC %sql
# MAGIC USE CATALOG ggrrr;
# MAGIC USE SCHEMA s11_ventas;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Consulta 1 — Total de ventas por categoría
# MAGIC *Pregunta a Genie: "¿Cuál es el total de ventas por categoría?"*

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   categoria,
# MAGIC   COUNT(*)                               AS total_productos,
# MAGIC   SUM(cantidad)                          AS unidades_vendidas,
# MAGIC   ROUND(SUM(precio * cantidad), 2)       AS total_ventas_usd,
# MAGIC   ROUND(AVG(precio), 2)                  AS precio_promedio
# MAGIC FROM ggrrr.s11_ventas.productos_s3
# MAGIC GROUP BY categoria
# MAGIC ORDER BY total_ventas_usd DESC;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Consulta 2 — Top 5 productos más vendidos en Lima
# MAGIC *Pregunta a Genie: "¿Qué productos tuvieron más ventas en Lima?"*

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   producto,
# MAGIC   categoria,
# MAGIC   precio,
# MAGIC   cantidad,
# MAGIC   ROUND(precio * cantidad, 2) AS ingreso_total
# MAGIC FROM ggrrr.s11_ventas.productos_s3
# MAGIC WHERE ciudad = 'Lima'
# MAGIC ORDER BY ingreso_total DESC
# MAGIC LIMIT 5;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Consulta 3 — Precio promedio por ciudad
# MAGIC *Pregunta a Genie: "¿Cuál es el precio promedio por ciudad?"*

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   ciudad,
# MAGIC   COUNT(*)                                 AS num_productos,
# MAGIC   ROUND(AVG(precio), 2)                    AS precio_promedio,
# MAGIC   MAX(precio)                              AS precio_maximo,
# MAGIC   ROUND(SUM(precio * cantidad), 2)         AS facturacion_total
# MAGIC FROM ggrrr.s11_ventas.productos_s3
# MAGIC GROUP BY ciudad
# MAGIC ORDER BY facturacion_total DESC;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Consulta 4 — Productos con precio mayor al promedio
# MAGIC *Pregunta a Genie: "¿Qué productos tienen precio mayor al promedio?"*

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   producto,
# MAGIC   categoria,
# MAGIC   ciudad,
# MAGIC   precio,
# MAGIC   ROUND(precio - (SELECT AVG(precio) FROM ggrrr.s11_ventas.productos_s3), 2) AS diferencia
# MAGIC FROM ggrrr.s11_ventas.productos_s3
# MAGIC WHERE precio > (SELECT AVG(precio) FROM ggrrr.s11_ventas.productos_s3)
# MAGIC ORDER BY precio DESC;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Consulta 5 — Ranking de productos por ciudad
# MAGIC *Pregunta a Genie: "Muéstrame el ranking de productos por ciudad"*

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   ciudad,
# MAGIC   producto,
# MAGIC   ROUND(precio * cantidad, 2)              AS ingreso,
# MAGIC   RANK() OVER (
# MAGIC     PARTITION BY ciudad
# MAGIC     ORDER BY precio * cantidad DESC
# MAGIC   )                                        AS ranking
# MAGIC FROM ggrrr.s11_ventas.productos_s3
# MAGIC ORDER BY ciudad, ranking;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Resumen — Consultas Genie Agents
# MAGIC | # | Pregunta | SQL |
# MAGIC |---|---|---|
# MAGIC | 1 | Total ventas por categoría | GROUP BY + SUM |
# MAGIC | 2 | Top 5 en Lima | WHERE + ORDER BY |
# MAGIC | 3 | Precio promedio por ciudad | GROUP BY + AVG |
# MAGIC | 4 | Productos sobre el promedio | Subconsulta |
# MAGIC | 5 | Ranking por ciudad | Window RANK() |
