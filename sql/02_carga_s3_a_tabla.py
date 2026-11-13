# Databricks notebook source
# MAGIC %md
# MAGIC # S11 — IPD: Conexión S3 → ggrrr.s11_ipd.deportistas_s3
# MAGIC **Sesión 11 | Databricks: S3 y Genie Agents**
# MAGIC Tatiana Conde — Proyecto IPD (Instituto Peruano del Deporte)
# MAGIC
# MAGIC Flujo: S3 Golden → ggrrr.s11_ipd.deportistas_s3 (Delta Lake)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 1: Leer CSV desde S3 con URL pre-firmada (Serverless compatible)

# COMMAND ----------

import boto3, pandas as pd, io, requests

# Credenciales AWS — no subir al repo
AWS_KEY    = ""   # tu Access Key ID
AWS_SECRET = ""   # tu Secret Access Key
BUCKET     = "tatiana-conde-databricks"
REGION     = "us-east-2"
KEY        = "golden/ipd/ipd_deportistas_real.csv"

# Generar URL pre-firmada (válida 1 hora, no requiere spark.conf)
s3 = boto3.client(
    's3',
    region_name          = REGION,
    aws_access_key_id    = AWS_KEY,
    aws_secret_access_key= AWS_SECRET
)

url = s3.generate_presigned_url(
    'get_object',
    Params     = {'Bucket': BUCKET, 'Key': KEY},
    ExpiresIn  = 3600
)
print("URL pre-firmada generada OK")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 2: Verificar archivos en S3

# COMMAND ----------

response = s3.list_objects_v2(Bucket=BUCKET, Prefix='golden/ipd/')
print("Archivos en S3:")
for obj in response.get('Contents', []):
    print(f"  {obj['Key']} — {round(obj['Size']/1024, 2)} KB")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 3: Leer CSV IPD desde S3 (Golden layer)

# COMMAND ----------

# Descargar CSV via URL pre-firmada y convertir a Spark DataFrame
resp     = requests.get(url)
df_pandas = pd.read_csv(io.BytesIO(resp.content))
df_ipd   = spark.createDataFrame(df_pandas)

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
