# Databricks notebook source
# MAGIC %md
# MAGIC # Notebook 04 - Volumen en Databricks (Punto 4)
# MAGIC **Sesión 08 | Databricks e Integraciones**
# MAGIC Juan Gabriel Condori Jara
# MAGIC
# MAGIC > Uso de **Volumes** en Unity Catalog para subir y gestionar imágenes y PDFs

# COMMAND ----------

# MAGIC %md
# MAGIC ## ¿Qué es un Volume en Databricks?
# MAGIC
# MAGIC Un **Volume** es una ubicación de almacenamiento gestionada dentro de Unity Catalog.
# MAGIC Permite guardar archivos no tabulares (imágenes, PDFs, CSVs, etc.) de forma organizada
# MAGIC dentro de un **Catalog** y **Schema** existente.
# MAGIC
# MAGIC **Ruta de acceso:** `/Volumes/<catalog>/<schema>/<volume_name>/`

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 1: Crear el Volume en Unity Catalog

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Primero verificamos los catálogos disponibles
# MAGIC SHOW CATALOGS;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Crear un schema dedicado para el volumen (si no existe)
# MAGIC CREATE SCHEMA IF NOT EXISTS main.s08_storage
# MAGIC COMMENT 'Schema para almacenamiento de archivos - Sesión 08';

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Crear el Volume dentro del schema
# MAGIC CREATE VOLUME IF NOT EXISTS main.s08_storage.archivos_multimedia
# MAGIC COMMENT 'Volumen para imágenes y PDFs - Juan Gabriel Condori Jara S08';

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Verificar que el Volume fue creado
# MAGIC SHOW VOLUMES IN main.s08_storage;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 2: Verificar la ruta del Volume

# COMMAND ----------

# La ruta del volumen sigue este patrón:
VOLUME_PATH = "/Volumes/main/s08_storage/archivos_multimedia"
print(f"Ruta del volumen: {VOLUME_PATH}")

# Listar archivos en el volumen (inicialmente vacío)
import os

try:
    files = dbutils.fs.ls(VOLUME_PATH)
    print(f"\nArchivos en el volumen ({len(files)} encontrados):")
    for f in files:
        print(f"  - {f.name} ({f.size} bytes)")
except Exception as e:
    print(f"El volumen está vacío o: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 3: Subir archivos al Volume
# MAGIC
# MAGIC ### Opción A: Desde la UI de Databricks
# MAGIC 1. Ir a **Catalog** en el menú lateral
# MAGIC 2. Expandir: `main` → `s08_storage` → `archivos_multimedia`
# MAGIC 3. Hacer clic en **"Upload to this volume"**
# MAGIC 4. Arrastrar o seleccionar tus imágenes (.jpg, .png) y PDFs (.pdf)
# MAGIC
# MAGIC ### Opción B: Desde el CLI de Databricks

# COMMAND ----------

# MAGIC %md
# MAGIC ```bash
# MAGIC # Subir una imagen desde tu máquina local
# MAGIC databricks fs cp imagen_evidencia.png dbfs:/Volumes/main/s08_storage/archivos_multimedia/
# MAGIC
# MAGIC # Subir un PDF
# MAGIC databricks fs cp documento_s08.pdf dbfs:/Volumes/main/s08_storage/archivos_multimedia/
# MAGIC
# MAGIC # Listar archivos subidos
# MAGIC databricks fs ls /Volumes/main/s08_storage/archivos_multimedia/
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 4: Leer y procesar archivos desde el Volume

# COMMAND ----------

# Ejemplo: Leer un CSV desde el volumen
# (descomenta cuando hayas subido un archivo)

# df_csv = spark.read.csv(
#     f"{VOLUME_PATH}/datos.csv",
#     header=True,
#     inferSchema=True
# )
# df_csv.show()

# Ejemplo: Leer un archivo de texto
# with open(f"{VOLUME_PATH}/notas.txt", "r") as f:
#     contenido = f.read()
#     print(contenido)

print("Para leer archivos del volumen, primero súbelos desde la UI o el CLI")
print(f"Ruta del volumen: {VOLUME_PATH}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 5: Crear un archivo de demostración en el Volume

# COMMAND ----------

# Crear un archivo de texto de demostración directamente desde el notebook
demo_content = """
==============================================
EVIDENCIA - SESIÓN 08 | DATABRICKS
==============================================
Estudiante: Juan Gabriel Condori Jara
Fecha: 26/09/2026
Tarea: AP4 - Databricks e Integraciones

Punto 4: Uso de Volumen para archivos
- Catalog: main
- Schema: s08_storage  
- Volume: archivos_multimedia
- Ruta: /Volumes/main/s08_storage/archivos_multimedia/

Archivos subidos:
- imagen_evidencia_01.png   (captura de pantalla CLI)
- imagen_evidencia_02.png   (captura de conexiones)
- reporte_s08.pdf           (reporte del trabajo)
==============================================
"""

# Guardar el archivo en el volumen
output_path = f"{VOLUME_PATH}/README_evidencia.txt"

with open(output_path.replace("/Volumes", "/dbfs/Volumes"), "w") as f:
    f.write(demo_content)

print(f"Archivo de evidencia creado en: {output_path}")

# COMMAND ----------

# Listar archivos después de crear el demo
files = dbutils.fs.ls(VOLUME_PATH)
print("Archivos en el volumen:")
for f in files:
    size_kb = f.size / 1024
    print(f"  📄 {f.name} - {size_kb:.2f} KB")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 6: Vincular el Volume con una tabla Delta

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Crear una tabla que registre los archivos subidos al volumen
# MAGIC CREATE OR REPLACE TABLE main.s08_storage.registro_archivos (
# MAGIC   id          INT,
# MAGIC   nombre      STRING,
# MAGIC   tipo        STRING,
# MAGIC   descripcion STRING,
# MAGIC   fecha_subida TIMESTAMP,
# MAGIC   ruta        STRING
# MAGIC )
# MAGIC COMMENT 'Registro de archivos subidos al volumen archivos_multimedia';

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Insertar registros de los archivos subidos
# MAGIC INSERT INTO main.s08_storage.registro_archivos VALUES
# MAGIC (1, 'imagen_evidencia_01.png', 'imagen', 'Captura de pantalla - instalación Databricks CLI', current_timestamp(), '/Volumes/main/s08_storage/archivos_multimedia/imagen_evidencia_01.png'),
# MAGIC (2, 'imagen_evidencia_02.png', 'imagen', 'Captura de pantalla - conexiones configuradas',    current_timestamp(), '/Volumes/main/s08_storage/archivos_multimedia/imagen_evidencia_02.png'),
# MAGIC (3, 'reporte_s08.pdf',         'pdf',    'Reporte completo de la Sesión 08',                 current_timestamp(), '/Volumes/main/s08_storage/archivos_multimedia/reporte_s08.pdf'),
# MAGIC (4, 'README_evidencia.txt',    'texto',  'Archivo de descripción creado desde notebook',     current_timestamp(), '/Volumes/main/s08_storage/archivos_multimedia/README_evidencia.txt');

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Verificar el registro
# MAGIC SELECT * FROM main.s08_storage.registro_archivos;

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ Notebook 04 completado
# MAGIC - Volume creado en Unity Catalog: `main.s08_storage.archivos_multimedia`
# MAGIC - Archivos subidos (imágenes y PDF)
# MAGIC - Tabla de registro vinculada al catálogo existente
