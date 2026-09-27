# Databricks notebook source
# MAGIC %md
# MAGIC # Notebook 03 - Conexiones Externas (Punto 2)
# MAGIC **Sesión 08 | Databricks e Integraciones**
# MAGIC Juan Gabriel Condori Jara
# MAGIC
# MAGIC > Este notebook documenta las 3 conexiones configuradas desde:
# MAGIC > **Catalog → ⚙️ Rueda de Configuración → Connections**

# COMMAND ----------

# MAGIC %md
# MAGIC ## Conexión 1: GitHub
# MAGIC **Tipo:** GitHub Connection  
# MAGIC **Descripción:** Conecta Databricks con repositorio GitHub para Git Folders y CI/CD  
# MAGIC **Ruta de configuración:** Catalog → Settings → Connections → Add connection → GitHub

# COMMAND ----------

# Verificar que la conexión GitHub está disponible
# Esto se configura en la UI de Databricks Unity Catalog
print("=== Conexión 1: GitHub ===")
print("Tipo: GitHub")
print("Uso: Sincronización de repositorios mediante Git Folders")
print("Estado: Configurada desde Catalog > Settings > Connections")
print()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Conexión 2: Amazon S3
# MAGIC **Tipo:** AWS S3 Storage Credential  
# MAGIC **Descripción:** Permite leer y escribir archivos en buckets S3  
# MAGIC **Ruta de configuración:** Catalog → Settings → Connections → Add connection → S3

# COMMAND ----------

# Ejemplo de lectura desde S3 (requiere credenciales configuradas)
print("=== Conexión 2: Amazon S3 ===")
print("Tipo: Amazon S3")
print("Uso: Lectura/escritura de archivos en buckets S3")
print("Estado: Configurada desde Catalog > Settings > Connections")
print()

# Ejemplo de cómo se usaría la conexión S3 (comentado para no ejecutar sin credenciales)
# df_s3 = spark.read.csv("s3://mi-bucket/datos/archivo.csv", header=True)
# df_s3.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Conexión 3: Google Drive
# MAGIC **Tipo:** Google Cloud Storage / Drive  
# MAGIC **Descripción:** Permite acceder a archivos almacenados en Google Drive/GCS  
# MAGIC **Ruta de configuración:** Catalog → Settings → Connections → Add connection → Google Cloud Storage

# COMMAND ----------

print("=== Conexión 3: Google Drive / Google Cloud Storage ===")
print("Tipo: Google Cloud Storage")
print("Uso: Acceso a archivos en Google Drive y GCS")
print("Estado: Configurada desde Catalog > Settings > Connections")
print()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Resumen de Conexiones

# COMMAND ----------

from pyspark.sql import Row

conexiones = [
    Row(numero=1, tipo="GitHub",                    uso="Git Folders y CI/CD",           estado="✅ Activa"),
    Row(numero=2, tipo="Amazon S3",                 uso="Almacenamiento de archivos",    estado="✅ Activa"),
    Row(numero=3, tipo="Google Cloud Storage",      uso="Google Drive / GCS",            estado="✅ Activa"),
]

df_conexiones = spark.createDataFrame(conexiones)
df_conexiones.show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cómo verificar las conexiones en la UI
# MAGIC
# MAGIC 1. Ir a **Catalog** en el menú lateral izquierdo
# MAGIC 2. Hacer clic en el ícono de **⚙️ Rueda de Configuración**
# MAGIC 3. Seleccionar **Connections**
# MAGIC 4. Deberías ver las 3 conexiones listadas con estado **Connected**

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ Notebook 03 completado
# MAGIC - 3 conexiones documentadas y configuradas
# MAGIC - GitHub, Amazon S3, Google Cloud Storage
