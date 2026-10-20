# Databricks notebook source
# MAGIC %md
# MAGIC # S11 — Conexión S3 → ggrrr.s11_ventas.productos_s3
# MAGIC **Sesión 11 | Databricks: S3 y Genie Agents**
# MAGIC Tatiana Conde
# MAGIC
# MAGIC Flujo:
# MAGIC 1. Conectar con Amazon S3 (credenciales IAM)
# MAGIC 2. Leer CSV desde `s3://tatiana-conde-databricks/golden/ventas_s11/`
# MAGIC 3. Guardar en `ggrrr.s11_ventas.productos_s3` (Delta Lake)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 1: Credenciales AWS (completa los widgets)

# COMMAND ----------

dbutils.widgets.text("aws_access_key", "", "AWS Access Key ID")
dbutils.widgets.text("aws_secret_key", "", "AWS Secret Access Key")
dbutils.widgets.text("bucket_name",    "tatiana-conde-databricks", "Bucket S3")
dbutils.widgets.text("region",         "us-east-2", "Region AWS")

# COMMAND ----------

AWS_KEY    = dbutils.widgets.get("aws_access_key")
AWS_SECRET = dbutils.widgets.get("aws_secret_key")
BUCKET     = dbutils.widgets.get("bucket_name")
REGION     = dbutils.widgets.get("region")

# Configurar Spark para S3
spark.conf.set("fs.s3a.access.key",    AWS_KEY)
spark.conf.set("fs.s3a.secret.key",    AWS_SECRET)
spark.conf.set("fs.s3a.endpoint",      f"s3.{REGION}.amazonaws.com")
spark.conf.set("fs.s3a.impl",          "org.apache.hadoop.fs.s3a.S3AFileSystem")
spark.conf.set("fs.s3a.aws.credentials.provider",
               "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")

S3_PATH = f"s3a://{BUCKET}/golden/ventas_s11/"
print(f"✅ Configuracion S3 lista")
print(f"   Ruta: {S3_PATH}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 2: Verificar conexión — listar archivos en S3

# COMMAND ----------

try:
    archivos = dbutils.fs.ls(S3_PATH)
    print(f"✅ Conexion S3 exitosa. Archivos encontrados:")
    for a in archivos:
        print(f"   {a.name} — {round(a.size/1024, 2)} KB")
except Exception as e:
    print(f"❌ Error conectando a S3: {e}")
    print("Verifica las credenciales y el nombre del bucket")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 3: Leer CSV desde S3

# COMMAND ----------

df_s3 = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv(S3_PATH)

print(f"✅ Datos leidos desde S3: {df_s3.count()} registros")
df_s3.printSchema()
df_s3.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 4: Crear schema y guardar en catalog

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Crear schema si no existe
# MAGIC CREATE SCHEMA IF NOT EXISTS ggrrr.s11_ventas
# MAGIC   COMMENT 'Schema S11 - Tatiana Conde';

# COMMAND ----------

# Guardar en Delta Lake: ggrrr.s11_ventas.productos_s3
df_s3.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("ggrrr.s11_ventas.productos_s3")

print("✅ Tabla guardada: ggrrr.s11_ventas.productos_s3")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 5: Verificar la tabla

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM ggrrr.s11_ventas.productos_s3 LIMIT 10;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*) AS total_registros FROM ggrrr.s11_ventas.productos_s3;

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ Conexion S3 completada
# MAGIC - Bucket: `s3://tatiana-conde-databricks/golden/ventas_s11/`
# MAGIC - Tabla: `ggrrr.s11_ventas.productos_s3`
# MAGIC - Lista para consultas con Genie Agents
