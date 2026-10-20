# Databricks notebook source
# MAGIC %md
# MAGIC # Notebook S11 — Consultas con Genie Agents (AI)
# MAGIC **Sesión 11 | Databricks: S3 y Genie Agents**
# MAGIC Tatiana Conde
# MAGIC
# MAGIC Este notebook contiene las **5 consultas mínimas** generadas con ayuda de
# MAGIC Databricks Genie (AI) sobre la tabla `ggrrr.s11_ventas.productos_s3`.
# MAGIC
# MAGIC > **¿Cómo usar Genie?**
# MAGIC > En el panel izquierdo de Databricks → **Genie Agents** → New Space →
# MAGIC > selecciona la tabla `ggrrr.s11_ventas.productos_s3` → haz preguntas
# MAGIC > en lenguaje natural. El SQL generado por Genie se copia aquí.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuración inicial

# COMMAND ----------

# Usar el catalog y schema correctos
spark.sql("USE CATALOG ggrrr")
spark.sql("USE SCHEMA s11_ventas")

print("✅ Usando: ggrrr.s11_ventas")
spark.sql("SHOW TABLES").show()

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## 🧞 Consulta 1 — Generada por Genie
# MAGIC **Pregunta a Genie:** *"¿Cuál es el total de ventas por categoría?"*

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Consulta 1: Total de ventas (precio × cantidad) por categoría
# MAGIC -- Generada con Genie Agents AI
# MAGIC SELECT
# MAGIC   categoria,
# MAGIC   COUNT(*)                                   AS total_productos,
# MAGIC   SUM(cantidad)                              AS unidades_vendidas,
# MAGIC   ROUND(SUM(precio * cantidad), 2)           AS total_ventas_usd,
# MAGIC   ROUND(AVG(precio), 2)                      AS precio_promedio
# MAGIC FROM ggrrr.s11_ventas.productos_s3
# MAGIC GROUP BY categoria
# MAGIC ORDER BY total_ventas_usd DESC;

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🧞 Consulta 2 — Generada por Genie
# MAGIC **Pregunta a Genie:** *"¿Qué productos tuvieron las mayores ventas en Lima?"*

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Consulta 2: Top 5 productos vendidos en Lima
# MAGIC -- Generada con Genie Agents AI
# MAGIC SELECT
# MAGIC   producto,
# MAGIC   categoria,
# MAGIC   precio,
# MAGIC   cantidad,
# MAGIC   ROUND(precio * cantidad, 2)  AS ingreso_total
# MAGIC FROM ggrrr.s11_ventas.productos_s3
# MAGIC WHERE ciudad = 'Lima'
# MAGIC ORDER BY ingreso_total DESC
# MAGIC LIMIT 5;

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🧞 Consulta 3 — Generada por Genie
# MAGIC **Pregunta a Genie:** *"¿Cuál es el promedio de precio por ciudad?"*

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Consulta 3: Precio promedio y máximo por ciudad
# MAGIC -- Generada con Genie Agents AI
# MAGIC SELECT
# MAGIC   ciudad,
# MAGIC   COUNT(*)                      AS num_productos,
# MAGIC   ROUND(AVG(precio), 2)         AS precio_promedio,
# MAGIC   MAX(precio)                   AS precio_maximo,
# MAGIC   MIN(precio)                   AS precio_minimo,
# MAGIC   ROUND(SUM(precio * cantidad), 2) AS facturacion_total
# MAGIC FROM ggrrr.s11_ventas.productos_s3
# MAGIC GROUP BY ciudad
# MAGIC ORDER BY facturacion_total DESC;

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🧞 Consulta 4 — Generada por Genie
# MAGIC **Pregunta a Genie:** *"¿Cuáles son los productos con precio mayor al promedio general?"*

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Consulta 4: Productos sobre el precio promedio (subconsulta)
# MAGIC -- Generada con Genie Agents AI
# MAGIC SELECT
# MAGIC   id,
# MAGIC   producto,
# MAGIC   categoria,
# MAGIC   precio,
# MAGIC   ROUND(precio - avg_general.precio_avg, 2) AS diferencia_con_promedio
# MAGIC FROM ggrrr.s11_ventas.productos_s3,
# MAGIC      (SELECT ROUND(AVG(precio), 2) AS precio_avg
# MAGIC       FROM ggrrr.s11_ventas.productos_s3) AS avg_general
# MAGIC WHERE precio > avg_general.precio_avg
# MAGIC ORDER BY precio DESC;

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🧞 Consulta 5 — Generada por Genie
# MAGIC **Pregunta a Genie:** *"Muéstrame el ranking de ventas por mes"*

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Consulta 5: Facturación mensual y ranking de productos
# MAGIC -- Generada con Genie Agents AI
# MAGIC SELECT
# MAGIC   DATE_FORMAT(fecha, 'yyyy-MM')          AS mes,
# MAGIC   producto,
# MAGIC   ciudad,
# MAGIC   ROUND(precio * cantidad, 2)            AS ingreso,
# MAGIC   RANK() OVER (
# MAGIC     PARTITION BY DATE_FORMAT(fecha, 'yyyy-MM')
# MAGIC     ORDER BY precio * cantidad DESC
# MAGIC   )                                      AS ranking_mes
# MAGIC FROM ggrrr.s11_ventas.productos_s3
# MAGIC ORDER BY mes, ranking_mes;

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Bonus: Consultas en Python (PySpark)

# COMMAND ----------

from pyspark.sql.functions import col, sum as _sum, avg, max, min, count, round as _round, rank
from pyspark.sql.window import Window

df = spark.table("ggrrr.s11_ventas.productos_s3")

# Resumen general
print("📊 Resumen General de Ventas")
df.withColumn("ingreso", _round(col("precio") * col("cantidad"), 2)) \
  .groupBy("categoria") \
  .agg(
      count("id").alias("productos"),
      _sum("cantidad").alias("unidades"),
      _round(_sum(col("precio") * col("cantidad")), 2).alias("total_usd")
  ) \
  .orderBy(col("total_usd").desc()) \
  .show()

# COMMAND ----------

# Window function: ranking por ciudad
print("🏆 Ranking de productos por ciudad")
window_ciudad = Window.partitionBy("ciudad").orderBy(col("precio").desc())
df.withColumn("rank_ciudad", rank().over(window_ciudad)) \
  .filter(col("rank_ciudad") <= 3) \
  .select("ciudad", "producto", "precio", "rank_ciudad") \
  .orderBy("ciudad", "rank_ciudad") \
  .show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ Consultas Genie completadas
# MAGIC | # | Pregunta a Genie | Tipo |
# MAGIC |---|---|---|
# MAGIC | 1 | Total de ventas por categoría | SQL Agregación |
# MAGIC | 2 | Top 5 productos en Lima | SQL Filtro + ORDER |
# MAGIC | 3 | Precio promedio por ciudad | SQL GROUP BY |
# MAGIC | 4 | Productos sobre precio promedio | SQL Subconsulta |
# MAGIC | 5 | Ranking de ventas por mes | SQL Window Function |
