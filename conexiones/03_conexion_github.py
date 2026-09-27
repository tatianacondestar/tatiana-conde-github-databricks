# Databricks notebook source
# MAGIC %md
# MAGIC # Conexión 3 — GitHub (Git Folder)
# MAGIC **Sesión 08 | Databricks e Integraciones**  
# MAGIC Juan Gabriel Condori Jara
# MAGIC
# MAGIC > Configura la conexión en:
# MAGIC > **Catalog → ⚙️ → Connections → Add → GitHub**

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 1: Crear Personal Access Token en GitHub
# MAGIC
# MAGIC 1. Ir a **github.com → tu foto → Settings**
# MAGIC 2. En el menú izquierdo: **Developer settings → Personal access tokens → Tokens (classic)**
# MAGIC 3. Clic en **Generate new token (classic)**
# MAGIC 4. Nombre: `databricks-s08`
# MAGIC 5. Scopes necesarios:
# MAGIC    - ✅ `repo` (acceso completo a repositorios)
# MAGIC    - ✅ `workflow` (para GitHub Actions)
# MAGIC 6. Clic en **Generate token** y copiar el token (empieza con `ghp_...`)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 2: Configurar la Conexión en Databricks Unity Catalog
# MAGIC
# MAGIC 1. Ir a **Catalog → ⚙️ → Connections → + Add**
# MAGIC 2. Elegir **GitHub**
# MAGIC 3. Completar:
# MAGIC    - **Connection name:** `github-s08`
# MAGIC    - **Personal Access Token:** `ghp_...` (el que generaste)
# MAGIC 4. Clic en **Test connection** → ✅ Connected
# MAGIC 5. Clic en **Create**

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 3: Crear el Git Folder (Repo) en Databricks
# MAGIC
# MAGIC 1. En Databricks, ir a **Workspace → Repos**
# MAGIC 2. Clic en **+ Add Repo**
# MAGIC 3. Completar:
# MAGIC    - **Git repository URL:** `https://github.com/TU_USUARIO/github-databricks`
# MAGIC    - **Git provider:** GitHub
# MAGIC    - **Personal access token:** (usar el mismo token)
# MAGIC 4. Clic en **Create Repo**
# MAGIC 5. El repositorio aparecerá sincronizado en el workspace

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 4: Verificar la sincronización

# COMMAND ----------

# Verificar que los notebooks del repo están accesibles desde el workspace
import subprocess

print("Verificando estructura del Git Folder sincronizado:")
print()

# Listar los archivos en el workspace (requiere que el Git Folder esté creado)
try:
    notebooks_repo = dbutils.fs.ls("/Repos/")
    print("Repos disponibles en el workspace:")
    for item in notebooks_repo:
        print(f"  {item.name}")
except Exception as e:
    print(f"Repos no accesibles via dbutils.fs: {e}")
    print("Usa la UI: Workspace → Repos para ver los Git Folders")

# COMMAND ----------

# Verificar la conexión GitHub via API de Databricks
try:
    # Obtener información del repo vinculado
    import requests

    token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
    host  = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiUrl().get()

    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(f"{host}/api/2.0/repos", headers=headers)

    if response.status_code == 200:
        repos = response.json().get("repos", [])
        print(f"Git Folders configurados ({len(repos)}):")
        print()
        for repo in repos:
            print(f"  Repo ID:  {repo.get('id')}")
            print(f"  URL:      {repo.get('url')}")
            print(f"  Branch:   {repo.get('branch')}")
            print(f"  Path:     {repo.get('path')}")
            print(f"  Provider: {repo.get('provider')}")
            print()
    else:
        print(f"Error: {response.status_code} - {response.text}")

except Exception as e:
    print(f"Error al consultar repos: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Paso 5: Hacer pull desde GitHub (actualizar el repo)

# COMMAND ----------

# Actualizar el repo desde GitHub (pull)
try:
    token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
    host  = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiUrl().get()

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Primero obtener el ID del repo
    response = requests.get(f"{host}/api/2.0/repos", headers=headers)
    repos = response.json().get("repos", [])

    if repos:
        repo_id = repos[0]["id"]

        # Hacer pull (actualizar desde GitHub)
        pull_response = requests.post(
            f"{host}/api/2.0/repos/{repo_id}",
            headers=headers,
            json={"branch": "main"}
        )

        if pull_response.status_code == 200:
            print("Repo actualizado exitosamente desde GitHub (branch: main)")
        else:
            print(f"Respuesta: {pull_response.status_code}")
    else:
        print("No hay repos configurados. Crea el Git Folder primero desde la UI.")

except Exception as e:
    print(f"Error: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Resumen de las 3 Conexiones Configuradas

# COMMAND ----------

from pyspark.sql import Row

conexiones = [
    Row(
        n=1,
        nombre="github-s08",
        tipo="GitHub",
        uso="Git Folders, CI/CD, sincronización de notebooks",
        ruta_config="Catalog → ⚙️ → Connections → github-s08"
    ),
    Row(
        n=2,
        nombre="rds-postgres-s08",
        tipo="PostgreSQL (Amazon RDS)",
        uso="Lectura/escritura de datos en base de datos relacional",
        ruta_config="Catalog → ⚙️ → Connections → rds-postgres-s08"
    ),
    Row(
        n=3,
        nombre="s3-databricks-s08",
        tipo="Amazon S3",
        uso="Almacenamiento de archivos CSV, Parquet e imágenes",
        ruta_config="Catalog → ⚙️ → Connections → s3-databricks-s08"
    ),
]

df = spark.createDataFrame(conexiones)
df.select("n", "nombre", "tipo", "uso").show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ Las 3 conexiones están configuradas y verificadas
# MAGIC
# MAGIC | # | Conexión | Tipo | Estado |
# MAGIC |---|----------|------|--------|
# MAGIC | 1 | github-s08 | GitHub | ✅ Activa |
# MAGIC | 2 | rds-postgres-s08 | PostgreSQL / Amazon RDS | ✅ Activa |
# MAGIC | 3 | s3-databricks-s08 | Amazon S3 | ✅ Activa |
# MAGIC
# MAGIC **Verificar en:** Catalog → ⚙️ → Connections
