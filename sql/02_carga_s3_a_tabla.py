# Databricks notebook source
# MAGIC %md
# MAGIC # S11 — Conexión S3 → ggrrr.s11_ventas.productos_s3
# MAGIC **Sesión 11 | Databricks: S3 y Genie Agents**
# MAGIC Tatiana Conde

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

# Configurar Hadoop para S3 (método alternativo compatible con Unity Catalog)
sc._jsc.hadoopConfiguration().set("fs.s3a.access.key",    AWS_KEY)
sc._jsc.hadoopConfiguration().set("fs.s3a.secret.key",    AWS_SECRET)
sc._jsc.hadoopConfiguration().set("fs.s3a.endpoint",      f"s3.{REGION}.amazonaws.com")
sc._jsc.hadoopConfiguration().set("fs.s3a.impl",          "org.apache.hadoop.fs.s3a.S3AFileSystem")
sc._jsc.hadoopConfiguration().set("fs.s3a.aws.credentials.provider",
                                   "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")

S3_PATH = f"s3a://{BUCKET}/golden/ventas_s11/"
print(f"Configuracion lista: {S3_PATH}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 2: Verificar conexion S3

# COMMAND ----------

try:
    archivos = dbutils.fs.ls(S3_PATH)
    print(f"Conexion S3 exitosa. Archivos:")
    for a in archivos:
        print(f"  {a.name} — {round(a.size/1024,2)} KB")
except Exception as e:
    print(f"Error: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 3: Leer CSV desde S3

# COMMAND ----------

df_s3 = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv(S3_PATH)

print(f"Registros leidos: {df_s3.count()}")
df_s3.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 4: Guardar en ggrrr.s11_ventas.productos_s3

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE SCHEMA IF NOT EXISTS ggrrr.s11_ventas;

# COMMAND ----------

df_s3.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("ggrrr.s11_ventas.productos_s3")

print("Tabla guardada: ggrrr.s11_ventas.productos_s3")

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM ggrrr.s11_ventas.productos_s3;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*) AS total FROM ggrrr.s11_ventas.productos_s3;
