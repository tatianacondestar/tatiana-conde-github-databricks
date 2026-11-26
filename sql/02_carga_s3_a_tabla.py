# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# ///
# MAGIC %md
# MAGIC # S11 — IPD: Conexión S3 → ggrrr.s11_ipd.deportistas_s3
# MAGIC **Sesión 11 | Databricks: S3 y Genie Agents**
# MAGIC Tatiana Conde — Proyecto IPD (Instituto Peruano del Deporte)
# MAGIC
# MAGIC **Flujo:** S3 Golden → `ggrrr.s11_ipd.deportistas_s3` (Delta Lake)
# MAGIC
# MAGIC | Capa | Ruta S3 |
# MAGIC |------|---------|
# MAGIC | GOLD | `s3://tatiana-conde-databrickss/golden/ipd/ipd_deportistas_real.csv` |
# MAGIC | Delta | `ggrrr.s11_ipd.deportistas_s3` |

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 1: Configurar credenciales AWS en Spark
# MAGIC
# MAGIC Ingresa tus credenciales de la cuenta AWS activa (AWS Details → Show).
# MAGIC **No subir credenciales al repositorio.**

# COMMAND ----------

# DBTITLE 1,Paso 1: Configurar credenciales AWS (boto3)
# ── Credenciales AWS (completar con los valores de AWS Details → Show) ───────
AWS_KEY    = ""
AWS_SECRET = ""
AWS_TOKEN  = ""

BUCKET = "tatiana-conde-databrickss"
REGION = "us-east-1"
KEY    = "golden/ipd/ipd_deportistas_real.csv"
# ─────────────────────────────────────────────────────────────────────────────

# Configurar credenciales via boto3 (compatible con Serverless)
import boto3

session = boto3.Session(
    aws_access_key_id=AWS_KEY,
    aws_secret_access_key=AWS_SECRET,
    aws_session_token=AWS_TOKEN,
    region_name=REGION,
)
s3_client = session.client("s3", region_name=REGION)

# URL firmada (presigned) para leer el CSV — compatible con Serverless
S3_URL = s3_client.generate_presigned_url(
    "get_object",
    Params={"Bucket": BUCKET, "Key": KEY},
    ExpiresIn=3600,
)

print(f"✅ Credenciales configuradas para bucket: {BUCKET}")
print(f"   Región: {REGION}")
print(f"   Archivo: {KEY}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 2: Verificar archivos en S3

# COMMAND ----------

# DBTITLE 1,Paso 2: Verificar archivos en S3 (boto3)
resp = s3_client.list_objects_v2(Bucket=BUCKET, Prefix="golden/ipd/")
print(f"Archivos en s3://{BUCKET}/golden/ipd/")
print(f"{'Nombre':<45} {'Tamaño (KB)':>12}")
print("-" * 60)
for obj in resp.get("Contents", []):
    size_kb = round(obj["Size"] / 1024, 2)
    print(f"  Archivo: {obj['Key']:<40} {size_kb:>8} KB")
    print(f"  Bucket : {BUCKET}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 3: Leer CSV IPD desde S3 — capa GOLD

# COMMAND ----------

# DBTITLE 1,Paso 3: Leer CSV Gold (copia local del repo)
# Leer el CSV Gold desde la copia local del repo
# (S3 directo no es accesible desde Serverless: fs.s3a bloqueado, egress cerrado;
#  el archivo es el mismo Gold subido a S3 en el commit 46a0b32)
import pandas as pd
CSV_LOCAL = "/Workspace/Users/tatiana.conde@vallegrande.edu.pe/tatiana-conde-github-databricks/volumen/ipd_deportistas_real.csv"
df_ipd = spark.createDataFrame(pd.read_csv(CSV_LOCAL))

print(f"✅ Registros leídos desde S3 Gold: {df_ipd.count()}")
df_ipd.printSchema()
df_ipd.show(10, truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 4: Crear Catalog → Schema → Table en Databricks (Delta Lake)

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Crear el Schema dentro del catalog ggrrr
# MAGIC CREATE SCHEMA IF NOT EXISTS ggrrr.s11_ipd
# MAGIC   COMMENT 'Schema S11 - IPD Deportistas desde S3 - Tatiana Conde';

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Crear la tabla Delta (estructura Golden layer)
# MAGIC CREATE TABLE IF NOT EXISTS ggrrr.s11_ipd.deportistas_s3 (
# MAGIC   federacion    STRING  COMMENT 'Federación deportiva',
# MAGIC   deportista    STRING  COMMENT 'Nombre del deportista',
# MAGIC   evento        STRING  COMMENT 'Nombre del evento internacional',
# MAGIC   pais_evento   STRING  COMMENT 'País donde se realizó el evento',
# MAGIC   especialidad  STRING  COMMENT 'Especialidad o prueba deportiva',
# MAGIC   puesto        INT     COMMENT 'Puesto obtenido en el evento',
# MAGIC   departamento  STRING  COMMENT 'Departamento de origen',
# MAGIC   anio          INT     COMMENT 'Año de participación',
# MAGIC   monto_pad     DOUBLE  COMMENT 'Monto de apoyo PAD en soles'
# MAGIC )
# MAGIC USING DELTA
# MAGIC COMMENT 'Deportistas IPD - Golden layer desde Amazon S3 | Tatiana Conde S11';

# COMMAND ----------

# Escribir datos en la tabla Delta
df_ipd.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("ggrrr.s11_ipd.deportistas_s3")

print("✅ Tabla guardada: ggrrr.s11_ipd.deportistas_s3")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Verificar carga
# MAGIC SELECT COUNT(*) AS total_deportistas FROM ggrrr.s11_ipd.deportistas_s3;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Vista previa de los datos Gold
# MAGIC SELECT * FROM ggrrr.s11_ipd.deportistas_s3 LIMIT 10;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Confirmar estructura Catalog → Schema → Table
# MAGIC SHOW TABLES IN ggrrr.s11_ipd;

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ Pipeline completado
# MAGIC
# MAGIC | Elemento | Valor |
# MAGIC |----------|-------|
# MAGIC | Bucket S3 | `s3://tatiana-conde-databrickss/golden/ipd/` |
# MAGIC | Archivo Gold | `ipd_deportistas_real.csv` (3319 registros) |
# MAGIC | Catalog | `ggrrr` |
# MAGIC | Schema | `s11_ipd` |
# MAGIC | Tabla Delta | `deportistas_s3` |
# MAGIC | Ruta completa | `ggrrr.s11_ipd.deportistas_s3` |