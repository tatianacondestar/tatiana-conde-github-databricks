# Databricks notebook source
# MAGIC %md
# MAGIC # Notebook 02 - Transformaciones y Pipeline ETL
# MAGIC **Sesión 08 | Databricks e Integraciones**
# MAGIC Juan Gabriel Condori Jara

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Lectura de datos desde Delta Lake

# COMMAND ----------

from pyspark.sql.functions import col, when, upper, concat, lit, current_timestamp
from pyspark.sql.types import StringType

# Leer la tabla creada en el notebook anterior
df = spark.read.table("default.personas_s08")
print(f"Registros leídos: {df.count()}")
df.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Transformaciones

# COMMAND ----------

# Transformación 1: Clasificar salarios
df_transformado = df.withColumn(
    "nivel_salario",
    when(col("salario") >= 5000, "Alto")
    .when(col("salario") >= 3500, "Medio")
    .otherwise("Bajo")
)

# Transformación 2: Nombre en mayúsculas
df_transformado = df_transformado.withColumn(
    "nombre_upper", upper(col("nombre"))
)

# Transformación 3: Columna combinada ciudad-carrera
df_transformado = df_transformado.withColumn(
    "ciudad_carrera",
    concat(col("ciudad"), lit(" - "), col("carrera"))
)

# Transformación 4: Timestamp de procesamiento
df_transformado = df_transformado.withColumn(
    "fecha_procesamiento", current_timestamp()
)

df_transformado.show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Filtros y selección

# COMMAND ----------

# Filtrar solo personas con salario alto o medio de Lima
df_lima = df_transformado.filter(
    (col("ciudad") == "Lima") & (col("nivel_salario").isin("Alto", "Medio"))
)
print("Personas con salario Alto/Medio en Lima:")
df_lima.show()

# COMMAND ----------

# Personas de Ingeniería o Tecnología ordenadas por salario
df_tech = df_transformado.filter(
    col("carrera").isin("Ingeniería", "Tecnología")
).orderBy(col("salario").desc())

print("Profesionales de Tecnología e Ingeniería (ordenados por salario):")
df_tech.select("nombre", "carrera", "ciudad", "salario", "nivel_salario").show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Guardar resultados transformados

# COMMAND ----------

# Guardar tabla transformada
df_transformado.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("default.personas_s08_transformado")

print("Tabla transformada guardada: default.personas_s08_transformado")

# COMMAND ----------

# Verificar
spark.sql("""
    SELECT nombre_upper, ciudad, carrera, salario, nivel_salario 
    FROM default.personas_s08_transformado
    ORDER BY salario DESC
""").show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ Notebook 02 completado exitosamente
# MAGIC - Datos leídos desde Delta Lake
# MAGIC - 4 transformaciones aplicadas
# MAGIC - Tabla transformada guardada
