# Databricks notebook source
# MAGIC %md
# MAGIC # S11 — IPD: Conexión S3 → ggrrr.s11_ipd.deportistas_s3
# MAGIC **Sesión 11 | Databricks: S3 y Genie Agents**
# MAGIC Tatiana Conde — Proyecto IPD (Instituto Peruano del Deporte)
# MAGIC
# MAGIC Flujo: S3 Golden → ggrrr.s11_ipd.deportistas_s3 (Delta Lake)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 1: Configurar credenciales AWS para Spark (s3a://)

# COMMAND ----------

# Credenciales AWS — no subir al repo
AWS_KEY    = ""   # tu Access Key ID
AWS_SECRET = ""   # tu Secret Access Key
BUCKET     = "tatiana-conde-databricks"
REGION     = "us-east-2"

# Configurar Spark para leer desde S3 con s3a://
spark.conf.set("fs.s3a.access.key",        AWS_KEY)
spark.conf.set("fs.s3a.secret.key",        AWS_SECRET)
spark.conf.set("fs.s3a.endpoint.region",   REGION)
spark.conf.set("fs.s3a.aws.credentials.provider",
               "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")

S3_PATH = f"s3a://{BUCKET}/golden/ipd/ipd_deportistas_real.csv"
print(f"Ruta S3: {S3_PATH}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 2: Verificar archivos en S3

# COMMAND ----------

files = dbutils.fs.ls(f"s3a://{BUCKET}/golden/ipd/")
print("Archivos en S3:")
for f in files:
    print(f"  {f.name} — {round(f.size/1024, 2)} KB")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 3: Leer CSV IPD desde S3 (Golden layer)

# COMMAND ----------

df_ipd = (spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .option("encoding", "UTF-8")
    .csv(S3_PATH)
)

print(f"Registros leidos: {df_ipd.count()}")
df_ipd.printSchema()
df_ipd.show(10, truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 4: Guardar en ggrrr.s11_ipd.deportistas_s3 (Delta Lake)

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
# MAGIC - Bucket S3: `s3://tatiana-conde-databricks/golden/ipd/`
# MAGIC - Tabla Delta: `ggrrr.s11_ipd.deportistas_s3`
# MAGIC - Deportistas IPD cargados correctamente
