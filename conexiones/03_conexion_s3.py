# Databricks notebook source
# MAGIC %md
# MAGIC # Conexión 1 — Amazon S3
# MAGIC **Sesión 08 | Databricks e Integraciones**  
# MAGIC Juan Gabriel Condori Jara
# MAGIC
# MAGIC > Antes de ejecutar este notebook, configura la conexión S3 en:
# MAGIC > **Catalog → ⚙️ → Connections → Add → Amazon S3**

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 1: Configurar credenciales AWS en el Cluster
# MAGIC
# MAGIC Ve a tu cluster → **Edit** → **Advanced options** → **Spark** → agrega:
# MAGIC ```
# MAGIC spark.hadoop.fs.s3a.access.key     TU_AWS_ACCESS_KEY_ID
# MAGIC spark.hadoop.fs.s3a.secret.key     TU_AWS_SECRET_ACCESS_KEY
# MAGIC spark.hadoop.fs.s3a.impl           org.apache.hadoop.fs.s3a.S3AFileSystem
# MAGIC spark.hadoop.fs.s3a.aws.credentials.provider  org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider
# MAGIC ```
# MAGIC
# MAGIC O usa los widgets del notebook (más seguro para demos):

# COMMAND ----------

# Widgets para ingresar credenciales sin hardcodearlas
dbutils.widgets.text("aws_access_key",    "", "AWS Access Key ID")
dbutils.widgets.text("aws_secret_key",    "", "AWS Secret Access Key")
dbutils.widgets.text("bucket_name",       "", "Nombre del bucket S3")
dbutils.widgets.text("bucket_region",     "us-east-1", "Región AWS")

# COMMAND ----------

# Leer valores de los widgets
AWS_ACCESS_KEY = dbutils.widgets.get("aws_access_key")
AWS_SECRET_KEY = dbutils.widgets.get("aws_secret_key")
BUCKET_NAME    = dbutils.widgets.get("bucket_name")
REGION         = dbutils.widgets.get("bucket_region")

# Configurar credenciales en Spark
spark.conf.set("fs.s3a.access.key",    AWS_ACCESS_KEY)
spark.conf.set("fs.s3a.secret.key",    AWS_SECRET_KEY)
spark.conf.set("fs.s3a.endpoint",      f"s3.{REGION}.amazonaws.com")
spark.conf.set("fs.s3a.impl",          "org.apache.hadoop.fs.s3a.S3AFileSystem")
spark.conf.set("fs.s3a.aws.credentials.provider",
               "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")

print(f"Credenciales configuradas para bucket: {BUCKET_NAME}")
print(f"Región: {REGION}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 2: Listar archivos en el bucket S3

# COMMAND ----------

# Listar archivos en la raíz del bucket
try:
    files = dbutils.fs.ls(f"s3a://{BUCKET_NAME}/")
    print(f"Archivos encontrados en s3a://{BUCKET_NAME}/")
    print(f"{'Nombre':<40} {'Tamaño (KB)':>12}")
    print("-" * 55)
    for f in files:
        size_kb = round(f.size / 1024, 2)
        print(f"{f.name:<40} {size_kb:>12}")
except Exception as e:
    print(f"Error al listar: {e}")
    print("Verifica que el bucket existe y las credenciales son correctas.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 3: Leer un CSV desde S3

# COMMAND ----------

# Leer un archivo CSV desde S3
# Cambia 'datos/archivo.csv' por la ruta real dentro de tu bucket
CSV_PATH = f"s3a://{BUCKET_NAME}/datos/"

try:
    df_s3 = spark.read \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .csv(CSV_PATH)

    print(f"Registros leídos desde S3: {df_s3.count()}")
    df_s3.printSchema()
    df_s3.show(10)
except Exception as e:
    # Si no hay CSV, crear uno de demo y subirlo
    print(f"No se encontró CSV en {CSV_PATH}")
    print("Creando datos de demo para subir a S3...")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 4: Crear datos y escribir en S3

# COMMAND ----------

from pyspark.sql import Row
from datetime import datetime

# Datos de ejemplo
datos_demo = [
    Row(id=1, producto="Laptop",   precio=1200.0, categoria="Tecnología", fecha="2026-09-26"),
    Row(id=2, producto="Monitor",  precio=350.0,  categoria="Tecnología", fecha="2026-09-26"),
    Row(id=3, producto="Teclado",  precio=80.0,   categoria="Periférico", fecha="2026-09-26"),
    Row(id=4, producto="Mouse",    precio=45.0,   categoria="Periférico", fecha="2026-09-26"),
    Row(id=5, producto="Audífonos",precio=120.0,  categoria="Audio",      fecha="2026-09-26"),
]

df_demo = spark.createDataFrame(datos_demo)
df_demo.show()

# COMMAND ----------

# Escribir como CSV en S3
OUTPUT_PATH = f"s3a://{BUCKET_NAME}/output/productos_s08/"

try:
    df_demo.write \
        .format("csv") \
        .option("header", "true") \
        .mode("overwrite") \
        .save(OUTPUT_PATH)

    print(f"Datos escritos exitosamente en S3:")
    print(f"  Ruta: {OUTPUT_PATH}")

    # Verificar que se escribió
    files_out = dbutils.fs.ls(OUTPUT_PATH)
    print(f"\nArchivos generados ({len(files_out)}):")
    for f in files_out:
        print(f"  {f.name} — {round(f.size/1024, 2)} KB")

except Exception as e:
    print(f"Error al escribir en S3: {e}")

# COMMAND ----------

# Escribir también como Parquet (formato columnar, más eficiente)
PARQUET_PATH = f"s3a://{BUCKET_NAME}/output/productos_s08_parquet/"

try:
    df_demo.write \
        .format("parquet") \
        .mode("overwrite") \
        .save(PARQUET_PATH)
    print(f"Parquet escrito en: {PARQUET_PATH}")
except Exception as e:
    print(f"Error: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 5: Leer de vuelta desde S3 y guardar en Delta Lake

# COMMAND ----------

# Leer el CSV que acabamos de escribir
df_desde_s3 = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv(OUTPUT_PATH)

print(f"Registros leídos desde S3: {df_desde_s3.count()}")
df_desde_s3.show()

# COMMAND ----------

# Guardar en Delta Lake para análisis posterior
df_desde_s3.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("default.productos_desde_s3")

print("Tabla Delta creada: default.productos_desde_s3")
spark.sql("SELECT * FROM default.productos_desde_s3").show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ Conexión S3 completada
# MAGIC - Credenciales configuradas
# MAGIC - Bucket listado correctamente
# MAGIC - CSV escrito y leído desde S3
# MAGIC - Parquet escrito en S3
# MAGIC - Datos importados a Delta Lake
