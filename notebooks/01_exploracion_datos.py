# Databricks notebook source
# MAGIC %md
# MAGIC # Notebook 01 - Exploración de Datos
# MAGIC **Sesión 08 | Databricks e Integraciones**
# MAGIC Juan Gabriel Condori Jara

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Configuración inicial del entorno

# COMMAND ----------

# Librerías estándar disponibles en Databricks
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, avg, max, min, desc
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType
import datetime

print("Entorno Databricks iniciado correctamente")
print(f"Spark versión: {spark.version}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Creación de datos de ejemplo

# COMMAND ----------

# Crear datos de ejemplo para demostración
data = [
    (1, "Juan",    "Lima",       28, 3500.0, "Ingeniería"),
    (2, "María",   "Arequipa",   32, 4200.0, "Medicina"),
    (3, "Carlos",  "Cusco",      25, 2800.0, "Administración"),
    (4, "Ana",     "Trujillo",   29, 3900.0, "Ingeniería"),
    (5, "Luis",    "Lima",       35, 5100.0, "Tecnología"),
    (6, "Sofía",   "Piura",      27, 3100.0, "Medicina"),
    (7, "Pedro",   "Arequipa",   31, 4500.0, "Tecnología"),
    (8, "Lucía",   "Lima",       24, 2600.0, "Administración"),
    (9, "Diego",   "Cusco",      38, 6000.0, "Ingeniería"),
    (10,"Valeria", "Trujillo",   26, 3300.0, "Tecnología"),
]

schema = StructType([
    StructField("id",        IntegerType(), True),
    StructField("nombre",    StringType(),  True),
    StructField("ciudad",    StringType(),  True),
    StructField("edad",      IntegerType(), True),
    StructField("salario",   DoubleType(),  True),
    StructField("carrera",   StringType(),  True),
])

df = spark.createDataFrame(data, schema)
df.printSchema()
df.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Análisis exploratorio básico

# COMMAND ----------

print(f"Total de registros: {df.count()}")
print(f"Columnas: {df.columns}")

# COMMAND ----------

# Estadísticas descriptivas
df.describe().show()

# COMMAND ----------

# Agrupación por ciudad
print("Promedio de salario por ciudad:")
df.groupBy("ciudad") \
  .agg(
      count("id").alias("total_personas"),
      avg("salario").alias("salario_promedio"),
      max("salario").alias("salario_maximo")
  ) \
  .orderBy(desc("salario_promedio")) \
  .show()

# COMMAND ----------

# Agrupación por carrera
print("Distribución por carrera:")
df.groupBy("carrera") \
  .agg(count("id").alias("cantidad")) \
  .orderBy(desc("cantidad")) \
  .show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Guardar resultados en Delta Lake

# COMMAND ----------

# Guardar como tabla Delta en el catálogo
df.write \
  .format("delta") \
  .mode("overwrite") \
  .saveAsTable("default.personas_s08")

print("Tabla guardada exitosamente en Delta Lake: default.personas_s08")

# COMMAND ----------

# Verificar que se guardó correctamente
spark.sql("SELECT * FROM default.personas_s08").show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ Notebook 01 completado exitosamente
# MAGIC - Datos creados y cargados en Spark
# MAGIC - Análisis exploratorio realizado
# MAGIC - Tabla guardada en Delta Lake
