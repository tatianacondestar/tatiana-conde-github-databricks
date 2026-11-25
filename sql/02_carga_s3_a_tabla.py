# Databricks notebook source
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
# MAGIC ## Paso 1: Configurar credenciales AWS
# MAGIC
# MAGIC Ingresa tus credenciales de la cuenta AWS activa (AWS Details → Show).
# MAGIC **No subir credenciales al repositorio.**

# COMMAND ----------

import boto3, pandas as pd, io, requests

# ── Credenciales AWS (completar con los valores de AWS Details) ──────────────
AWS_KEY     = ""   # Access Key ID
AWS_SECRET  = ""   # Secret Access Key
AWS_TOKEN   = ""   # Session Token (si usas voclabs / lab account)

BUCKET  = "tatiana-conde-databrickss"   # nuevo bucket
REGION  = "us-east-1"
KEY     = "golden/ipd/ipd_deportistas_real.csv"
# ─────────────────────────────────────────────────────────────────────────────

s3_client = boto3.client(
    's3',
    region_name           = REGION,
    aws_access_key_id     = AWS_KEY,
    aws_secret_access_key = AWS_SECRET,
    **({"aws_session_token": AWS_TOKEN} if AWS_TOKEN else {}),
)

# Verificar conexión
try:
    s3_client.head_bucket(Bucket=BUCKET)
    print(f"✅ Conexión exitosa con bucket: {BUCKET}")
except Exception as e:
    raise RuntimeError(f"❌ Error al conectar con S3: {e}\n"
                       "→ Verifica que las credenciales sean correctas y el bucket exista.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 2: Verificar archivos en S3

# COMMAND ----------

response = s3_client.list_objects_v2(Bucket=BUCKET, Prefix="golden/ipd/")
contenidos = response.get("Contents", [])

if contenidos:
    print(f"Archivos en s3://{BUCKET}/golden/ipd/")
    for obj in contenidos:
        print(f"  Archivo: {obj['Key']}")
        print(f"  Tamaño : {round(obj['Size']/1024, 2)} KB")
        print(f"  Bucket : {BUCKET}")
else:
    print(f"⚠️  No se encontraron archivos en s3://{BUCKET}/golden/ipd/")
    print("   → Ejecuta primero el paso de carga del CSV (celda siguiente).")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 2b: Subir CSV al bucket S3 (solo si el bucket está vacío)
# MAGIC
# MAGIC Ejecuta esta celda **una sola vez** para cargar el archivo Gold al nuevo bucket.

# COMMAND ----------

import urllib.request, tempfile, os

# URL pública del CSV en GitHub (rama main)
CSV_GITHUB_URL = (
    "https://raw.githubusercontent.com/tatianacondestar/"
    "tatiana-conde-github-databricks/main/volumen/ipd_deportistas_real.csv"
)

# Descargar desde GitHub
print("Descargando CSV desde GitHub...")
resp_gh = requests.get(CSV_GITHUB_URL, timeout=30)
resp_gh.raise_for_status()
csv_bytes = resp_gh.content
print(f"  Tamaño descargado: {round(len(csv_bytes)/1024, 2)} KB")

# Subir a S3
s3_client.put_object(
    Bucket      = BUCKET,
    Key         = KEY,
    Body        = csv_bytes,
    ContentType = "text/csv",
)
print(f"✅ Archivo subido a s3://{BUCKET}/{KEY}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 3: Leer CSV IPD desde S3 — capa GOLD

# COMMAND ----------

# Generar URL pre-firmada (válida 1 hora, compatible con Serverless)
url_presignada = s3_client.generate_presigned_url(
    "get_object",
    Params    = {"Bucket": BUCKET, "Key": KEY},
    ExpiresIn = 3600,
)
print("URL pre-firmada generada OK")

# Descargar y convertir a Spark DataFrame
resp      = requests.get(url_presignada, timeout=60)
resp.raise_for_status()
df_pandas = pd.read_csv(io.BytesIO(resp.content))
df_ipd    = spark.createDataFrame(df_pandas)

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
# MAGIC | Archivo Gold | `ipd_deportistas_real.csv` (50 registros) |
# MAGIC | Catalog | `ggrrr` |
# MAGIC | Schema | `s11_ipd` |
# MAGIC | Tabla Delta | `deportistas_s3` |
# MAGIC | Ruta completa | `ggrrr.s11_ipd.deportistas_s3` |
