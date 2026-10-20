# Databricks notebook source
# MAGIC %md
# MAGIC # Notebook S11 — Conexión S3 → catalog.schema.tabla
# MAGIC **Sesión 11 | Databricks: S3 y Genie Agents**
# MAGIC Tatiana Conde
# MAGIC
# MAGIC Este notebook:
# MAGIC 1. Se conecta a Amazon S3 con credenciales personales
# MAGIC 2. Lee un archivo CSV desde S3
# MAGIC 3. Guarda los datos en `tatiana_catalog.s11_ventas.productos_s3`

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 1: Ingresar credenciales AWS (widgets)
# MAGIC
# MAGIC > Completa los campos arriba antes de ejecutar. Nunca hardcodees tus claves.

# COMMAND ----------

# Widgets para credenciales (se ingresan de forma segura en la UI)
dbutils.widgets.text("aws_access_key", "", "🔑 AWS Access Key ID")
dbutils.widgets.text("aws_secret_key", "", "🔒 AWS Secret Access Key")
dbutils.widgets.text("bucket_name",    "tatiana-conde-databricks", "🪣 Nombre del bucket S3")
dbutils.widgets.text("region",         "us-east-1", "🌎 Región AWS")
dbutils.widgets.text("csv_path",       "datos/ventas.csv", "📄 Ruta del CSV en S3")

# COMMAND ----------

# Leer valores de widgets
AWS_KEY    = dbutils.widgets.get("aws_access_key")
AWS_SECRET = dbutils.widgets.get("aws_secret_key")
BUCKET     = dbutils.widgets.get("bucket_name")
REGION     = dbutils.widgets.get("region")
CSV_FILE   = dbutils.widgets.get("csv_path")

# Configurar Spark con credenciales S3
spark.conf.set("fs.s3a.access.key",    AWS_KEY)
spark.conf.set("fs.s3a.secret.key",    AWS_SECRET)
spark.conf.set("fs.s3a.endpoint",      f"s3.{REGION}.amazonaws.com")
spark.conf.set("fs.s3a.impl",          "org.apache.hadoop.fs.s3a.S3AFileSystem")
spark.conf.set("fs.s3a.aws.credentials.provider",
               "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")

print(f"✅ Configuración S3 lista")
print(f"   Bucket : s3a://{BUCKET}/")
print(f"   Archivo: {CSV_FILE}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 2: Crear datos de ejemplo en S3 (si no tienes un CSV propio)

# COMMAND ----------

from pyspark.sql import Row
from pyspark.sql.functions import col, to_date, lit
import datetime

# Datos de ventas de ejemplo — Golden/Silver layer
ventas_data = [
    Row(id=1,  producto="Laptop Pro",      precio=1200.0, categoria="Tecnología",  cantidad=5,  ciudad="Lima",      fecha="2026-09-01"),
    Row(id=2,  producto="Monitor 4K",      precio=350.0,  categoria="Tecnología",  cantidad=8,  ciudad="Arequipa",  fecha="2026-09-02"),
    Row(id=3,  producto="Teclado Mec.",    precio=80.0,   categoria="Periférico",  cantidad=15, ciudad="Cusco",     fecha="2026-09-03"),
    Row(id=4,  producto="Mouse Ergon.",    precio=45.0,   categoria="Periférico",  cantidad=20, ciudad="Lima",      fecha="2026-09-04"),
    Row(id=5,  producto="Audífonos BT",    precio=120.0,  categoria="Audio",       cantidad=12, ciudad="Trujillo",  fecha="2026-09-05"),
    Row(id=6,  producto="Tablet S9",       precio=600.0,  categoria="Tecnología",  cantidad=3,  ciudad="Piura",     fecha="2026-09-06"),
    Row(id=7,  producto="Impresora HP",    precio=280.0,  categoria="Oficina",     cantidad=7,  ciudad="Lima",      fecha="2026-09-07"),
    Row(id=8,  producto="Webcam HD",       precio=90.0,   categoria="Periférico",  cantidad=18, ciudad="Cusco",     fecha="2026-09-08"),
    Row(id=9,  producto="SSD 1TB",         precio=110.0,  categoria="Almacen.",    cantidad=25, ciudad="Arequipa",  fecha="2026-09-09"),
    Row(id=10, producto="Router WiFi 6",   precio=160.0,  categoria="Redes",       cantidad=10, ciudad="Lima",      fecha="2026-09-10"),
    Row(id=11, producto="Laptop Core i5",  precio=950.0,  categoria="Tecnología",  cantidad=6,  ciudad="Trujillo",  fecha="2026-09-11"),
    Row(id=12, producto="Proyector LED",   precio=420.0,  categoria="Oficina",     cantidad=4,  ciudad="Lima",      fecha="2026-09-12"),
    Row(id=13, producto="Disco Externo",   precio=75.0,   categoria="Almacen.",    cantidad=30, ciudad="Arequipa",  fecha="2026-09-13"),
    Row(id=14, producto="Smart TV 55\"",   precio=800.0,  categoria="Tecnología",  cantidad=2,  ciudad="Lima",      fecha="2026-09-14"),
    Row(id=15, producto="Cámara Mirr.",    precio=1500.0, categoria="Fotografía",  cantidad=1,  ciudad="Cusco",     fecha="2026-09-15"),
]

df_ventas = spark.createDataFrame(ventas_data) \
    .withColumn("fecha", to_date(col("fecha"), "yyyy-MM-dd"))

print(f"✅ Dataset creado: {df_ventas.count()} registros")
df_ventas.show(5)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 3: Subir CSV a S3 (Golden layer)

# COMMAND ----------

S3_OUTPUT = f"s3a://{BUCKET}/golden/ventas_s11/"

try:
    df_ventas.write \
        .format("csv") \
        .option("header", "true") \
        .mode("overwrite") \
        .save(S3_OUTPUT)
    print(f"✅ CSV escrito en S3: {S3_OUTPUT}")

    archivos = dbutils.fs.ls(S3_OUTPUT)
    for a in archivos:
        print(f"   📄 {a.name} — {round(a.size/1024, 2)} KB")
except Exception as e:
    print(f"⚠️  Error S3: {e}")
    print("Continuando con datos en memoria...")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 4: Leer desde S3 y cargar en catalog.schema.tabla

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Asegurar que el catalog y schema existen
# MAGIC CREATE CATALOG IF NOT EXISTS tatiana_catalog;
# MAGIC CREATE SCHEMA  IF NOT EXISTS tatiana_catalog.s11_ventas;
# MAGIC USE CATALOG tatiana_catalog;
# MAGIC USE SCHEMA   s11_ventas;

# COMMAND ----------

# Leer desde S3 (o usar df_ventas si S3 no está configurado aún)
try:
    df_desde_s3 = spark.read \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .csv(S3_OUTPUT)
    print("✅ Datos leídos desde S3")
except Exception:
    df_desde_s3 = df_ventas
    print("ℹ️  Usando datos en memoria (S3 no conectado aún)")

df_desde_s3.show()

# COMMAND ----------

# Guardar en la tabla Delta del catalog
df_desde_s3.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("tatiana_catalog.s11_ventas.productos_s3")

print("✅ Tabla cargada: tatiana_catalog.s11_ventas.productos_s3")

# COMMAND ----------

# Verificar la carga
spark.sql("SELECT * FROM tatiana_catalog.s11_ventas.productos_s3").show()
print(f"Total registros: {spark.sql('SELECT COUNT(*) FROM tatiana_catalog.s11_ventas.productos_s3').collect()[0][0]}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ Pipeline S3 → Catalog completado
# MAGIC - Datos escritos en S3 (Golden layer)
# MAGIC - Tabla Delta creada en `tatiana_catalog.s11_ventas.productos_s3`
# MAGIC - Lista para consultas con Genie Agents
