# Databricks notebook source
# MAGIC %md
# MAGIC # Conexión 2 — Amazon RDS (PostgreSQL)
# MAGIC **Sesión 08 | Databricks e Integraciones**  
# MAGIC Juan Gabriel Condori Jara
# MAGIC
# MAGIC > Antes de ejecutar, crea la conexión en:
# MAGIC > **Catalog → ⚙️ → Connections → Add → PostgreSQL**

# COMMAND ----------

# MAGIC %md
# MAGIC ## Cómo crear una RDS PostgreSQL en AWS (si no tienes)
# MAGIC
# MAGIC 1. Ir a **AWS Console → RDS → Create database**
# MAGIC 2. Elegir **PostgreSQL**
# MAGIC 3. Template: **Free tier**
# MAGIC 4. DB instance identifier: `databricks-s08`
# MAGIC 5. Master username: `postgres`
# MAGIC 6. Master password: (anotar bien)
# MAGIC 7. **Public access: Yes** (para poder conectar desde Databricks)
# MAGIC 8. En Security Group: abrir el puerto **5432** para `0.0.0.0/0` (solo para demo)
# MAGIC 9. Esperar ~5 min a que el estado sea **Available**
# MAGIC 10. Copiar el **Endpoint** (ej: `databricks-s08.xxxx.us-east-1.rds.amazonaws.com`)

# COMMAND ----------

# Widgets para ingresar credenciales
dbutils.widgets.text("rds_host",     "", "RDS Endpoint (host)")
dbutils.widgets.text("rds_port",     "5432", "Puerto")
dbutils.widgets.text("rds_database", "postgres", "Nombre de la base de datos")
dbutils.widgets.text("rds_user",     "postgres", "Usuario")
dbutils.widgets.text("rds_password", "", "Contraseña")

# COMMAND ----------

# Leer credenciales
RDS_HOST     = dbutils.widgets.get("rds_host")
RDS_PORT     = dbutils.widgets.get("rds_port")
RDS_DATABASE = dbutils.widgets.get("rds_database")
RDS_USER     = dbutils.widgets.get("rds_user")
RDS_PASSWORD = dbutils.widgets.get("rds_password")

# Construir JDBC URL
JDBC_URL = f"jdbc:postgresql://{RDS_HOST}:{RDS_PORT}/{RDS_DATABASE}"

print(f"JDBC URL: jdbc:postgresql://{RDS_HOST}:{RDS_PORT}/{RDS_DATABASE}")
print("Contraseña: ****")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 1: Crear tabla en RDS y cargar datos

# COMMAND ----------

# Propiedades de conexión JDBC
connection_properties = {
    "user":     RDS_USER,
    "password": RDS_PASSWORD,
    "driver":   "org.postgresql.Driver"
}

# COMMAND ----------

# Crear un DataFrame con datos para insertar en RDS
from pyspark.sql import Row

estudiantes = [
    Row(id=1, nombre="Juan Gabriel",  carrera="Ingeniería IA",   nota=18.5, semestre=8),
    Row(id=2, nombre="María López",   carrera="Ciencia de Datos",nota=17.0, semestre=6),
    Row(id=3, nombre="Carlos Ríos",   carrera="Ingeniería IA",   nota=19.0, semestre=8),
    Row(id=4, nombre="Ana Torres",    carrera="Estadística",     nota=16.5, semestre=4),
    Row(id=5, nombre="Luis Mamani",   carrera="Ciencia de Datos",nota=18.0, semestre=6),
]

df_estudiantes = spark.createDataFrame(estudiantes)
df_estudiantes.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 2: Escribir datos en RDS (JDBC)

# COMMAND ----------

try:
    df_estudiantes.write \
        .format("jdbc") \
        .option("url",      JDBC_URL) \
        .option("dbtable",  "estudiantes_s08") \
        .option("user",     RDS_USER) \
        .option("password", RDS_PASSWORD) \
        .option("driver",   "org.postgresql.Driver") \
        .mode("overwrite") \
        .save()

    print("Tabla 'estudiantes_s08' creada y datos insertados en RDS PostgreSQL")

except Exception as e:
    print(f"Error al escribir en RDS: {e}")
    print("\nVerifica:")
    print("  1. El endpoint RDS es correcto")
    print("  2. El Security Group tiene el puerto 5432 abierto")
    print("  3. Las credenciales son correctas")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 3: Leer datos desde RDS

# COMMAND ----------

try:
    df_desde_rds = spark.read \
        .format("jdbc") \
        .option("url",      JDBC_URL) \
        .option("dbtable",  "estudiantes_s08") \
        .option("user",     RDS_USER) \
        .option("password", RDS_PASSWORD) \
        .option("driver",   "org.postgresql.Driver") \
        .load()

    print(f"Registros leídos desde RDS: {df_desde_rds.count()}")
    df_desde_rds.show()

except Exception as e:
    print(f"Error al leer desde RDS: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 4: Ejecutar una query SQL directamente sobre RDS

# COMMAND ----------

# Query con filtro directo en PostgreSQL (pushdown)
QUERY = "(SELECT * FROM estudiantes_s08 WHERE nota >= 18.0) AS top_estudiantes"

try:
    df_top = spark.read \
        .format("jdbc") \
        .option("url",      JDBC_URL) \
        .option("dbtable",  QUERY) \
        .option("user",     RDS_USER) \
        .option("password", RDS_PASSWORD) \
        .option("driver",   "org.postgresql.Driver") \
        .load()

    print("Estudiantes con nota >= 18:")
    df_top.show()

except Exception as e:
    print(f"Error: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 5: Guardar datos de RDS en Delta Lake

# COMMAND ----------

try:
    df_desde_rds.write \
        .format("delta") \
        .mode("overwrite") \
        .saveAsTable("default.estudiantes_desde_rds")

    print("Tabla Delta creada: default.estudiantes_desde_rds")
    spark.sql("SELECT * FROM default.estudiantes_desde_rds ORDER BY nota DESC").show()

except Exception as e:
    print(f"Error: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 6: Configurar la Conexión desde Unity Catalog (UI)
# MAGIC
# MAGIC Para registrar la conexión oficialmente en Databricks:
# MAGIC
# MAGIC 1. Ir a **Catalog → ⚙️ (rueda) → Connections → + Add**
# MAGIC 2. Elegir **PostgreSQL**
# MAGIC 3. Completar:
# MAGIC    - **Connection name:** `rds-postgres-s08`
# MAGIC    - **Host:** tu endpoint RDS
# MAGIC    - **Port:** `5432`
# MAGIC    - **Database:** `postgres`
# MAGIC    - **Username:** `postgres`
# MAGIC    - **Password:** tu contraseña
# MAGIC 4. Clic en **Test connection** → debe decir ✅ Connected
# MAGIC 5. Clic en **Create**

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ Conexión RDS PostgreSQL completada
# MAGIC - Tabla creada en RDS via JDBC
# MAGIC - Datos escritos desde Databricks → RDS
# MAGIC - Datos leídos desde RDS → Databricks
# MAGIC - Query con filtro ejecutada sobre PostgreSQL
# MAGIC - Datos importados a Delta Lake
