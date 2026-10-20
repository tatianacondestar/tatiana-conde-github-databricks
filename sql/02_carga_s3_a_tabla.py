# Databricks notebook source
# MAGIC %md
# MAGIC # S11 — IPD: Conexión S3 → ggrrr.s11_ipd.deportistas_s3
# MAGIC **Sesión 11 | Databricks: S3 y Genie Agents**
# MAGIC Tatiana Conde — Proyecto IPD (Instituto Peruano del Deporte)
# MAGIC
# MAGIC Flujo: S3 Golden → ggrrr.s11_ipd.deportistas_s3 (Delta Lake)

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

# Configurar Hadoop para S3 (compatible con Unity Catalog)
sc._jsc.hadoopConfiguration().set("fs.s3a.access.key",    AWS_KEY)
sc._jsc.hadoopConfiguration().set("fs.s3a.secret.key",    AWS_SECRET)
sc._jsc.hadoopConfiguration().set("fs.s3a.endpoint",      f"s3.{REGION}.amazonaws.com")
sc._jsc.hadoopConfiguration().set("fs.s3a.impl",          "org.apache.hadoop.fs.s3a.S3AFileSystem")
sc._jsc.hadoopConfiguration().set("fs.s3a.aws.credentials.provider",
                                   "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
S3_PATH = f"s3a://{BUCKET}/golden/ipd/"
print(f"Configuracion S3 lista: {S3_PATH}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 2: Verificar conexion y listar archivos

# COMMAND ----------

try:
    archivos = dbutils.fs.ls(S3_PATH)
    print("Conexion S3 exitosa. Archivos en Golden layer:")
    for a in archivos:
        print(f"  {a.name} — {round(a.size/1024,2)} KB")
except Exception as e:
    print(f"Error conectando S3: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 3: Leer CSV IPD desde S3

# COMMAND ----------

df_ipd = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv(S3_PATH)

print(f"Registros IPD leidos desde S3: {df_ipd.count()}")
df_ipd.printSchema()
df_ipd.show(10)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 4: Crear schema y guardar en Delta Lake

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE SCHEMA IF NOT EXISTS ggrrr.s11_ipd
# MAGIC   COMMENT 'Schema S11 IPD - Tatiana Conde';

# COMMAND ----------

df_ipd.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("ggrrr.s11_ipd.deportistas_s3")

print("Tabla guardada: ggrrr.s11_ipd.deportistas_s3")

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM ggrrr.s11_ipd.deportistas_s3 LIMIT 10;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*) AS total_deportistas FROM ggrrr.s11_ipd.deportistas_s3;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Pipeline completado
# MAGIC - Bucket S3: `tatiana-conde-databricks/golden/ipd/`
# MAGIC - Tabla Delta: `ggrrr.s11_ipd.deportistas_s3`
# MAGIC - Lista para consultas con Genie Agents
