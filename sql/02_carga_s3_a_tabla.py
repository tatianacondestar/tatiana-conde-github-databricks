# Databricks notebook source
# MAGIC %md
# MAGIC # S11 — IPD: Conexión S3 → ggrrr.s11_ipd.deportistas_s3
# MAGIC **Sesión 11 | Databricks: S3 y Genie Agents**
# MAGIC Tatiana Conde — Proyecto IPD (Instituto Peruano del Deporte)
# MAGIC
# MAGIC Flujo: S3 Golden → ggrrr.s11_ipd.deportistas_s3 (Delta Lake)
# MAGIC
# MAGIC **Instrucciones:** Ingresa tus credenciales AWS en los widgets de arriba antes de ejecutar.

# COMMAND ----------

dbutils.widgets.text("aws_access_key", "", "AWS Access Key ID")
dbutils.widgets.text("aws_secret_key", "", "AWS Secret Access Key")
dbutils.widgets.text("bucket_name",    "tatiana-conde-databricks", "Bucket S3")
dbutils.widgets.text("region",         "us-east-2", "Region AWS")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 1: Conectar con Amazon S3 usando boto3

# COMMAND ----------

import boto3, pandas as pd, io

AWS_KEY    = dbutils.widgets.get("aws_access_key")
AWS_SECRET = dbutils.widgets.get("aws_secret_key")
BUCKET     = dbutils.widgets.get("bucket_name")
REGION     = dbutils.widgets.get("region")

s3 = boto3.client('s3',
    region_name=REGION,
    aws_access_key_id=AWS_KEY,
    aws_secret_access_key=AWS_SECRET
)
print(f"Conexion S3 lista: s3://{BUCKET}/golden/ipd/")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 2: Verificar archivos en S3

# COMMAND ----------

response = s3.list_objects_v2(Bucket=BUCKET, Prefix='golden/ipd/')
for obj in response.get('Contents', []):
    print(f"  {obj['Key']} — {round(obj['Size']/1024, 2)} KB")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 3: Leer CSV IPD desde S3

# COMMAND ----------

obj = s3.get_object(Bucket=BUCKET, Key='golden/ipd/ventas_s11.csv')
df_pandas = pd.read_csv(io.BytesIO(obj['Body'].read()))
df_ipd = spark.createDataFrame(df_pandas)

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
