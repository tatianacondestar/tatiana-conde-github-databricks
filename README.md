# github-databricks — S08 AP4
**Estudiante:** Juan Gabriel Condori Jara  
**Curso:** Fundamentos de Inteligencia Artificial — ASE242_FIA  
**Sesión:** 08 | Databricks e Integraciones  

---

## Estructura del proyecto

```
github-databricks/
├── .github/
│   └── workflows/
│       └── pipeline.yml          ← Pipeline CI/CD GitHub Actions
├── notebooks/
│   ├── 01_exploracion_datos.py   ← Carga y análisis de datos en Spark
│   └── 02_transformaciones.py    ← Pipeline ETL con Delta Lake
├── conexiones/
│   └── 03_conexiones_externas.py ← Documentación de las 3 conexiones
├── volumen/
│   └── 04_volumen_archivos.py    ← Gestión de Volume para imágenes/PDFs
├── cli/
│   ├── databricks_cli_demo.sh         ← Demo CLI Linux/Mac
│   └── databricks_cli_demo_windows.ps1← Demo CLI Windows
├── databricks.yml                ← Configuración del bundle Databricks
└── README.md
```

---

## Punto 1 — GitHub Actions + Git Folder en Databricks

### Configurar los Secrets en GitHub

Antes de que el pipeline funcione, agrega estas variables en tu repo:  
`Settings → Secrets and variables → Actions → New repository secret`

| Secret              | Valor de ejemplo                                    |
|---------------------|-----------------------------------------------------|
| `DATABRICKS_HOST`   | `https://dbc-8f7207fa-f694.cloud.databricks.com`   |
| `DATABRICKS_TOKEN`  | `dapi1234567890abcdef...`                           |

### Cómo genera el token en Databricks

1. Inicia sesión en tu workspace de Databricks
2. Ve a **Settings → Developer → Access Tokens**
3. Clic en **Generate new token**
4. Ponle un nombre (ej. `github-actions-s08`) y copia el token

### Configurar el Git Folder en Databricks

1. En Databricks, ve a **Repos** en el menú lateral
2. Clic en **Add Repo**
3. Pega la URL de tu repositorio GitHub: `https://github.com/TU_USUARIO/github-databricks`
4. Clic en **Create Repo**

### Cómo funciona el pipeline

```
Push a main
     │
     ▼
┌─────────────┐     ┌──────────────────────┐     ┌───────────────────┐
│  validate   │────▶│  sync-to-databricks  │────▶│   deploy-prod     │
│             │     │                      │     │                   │
│ Valida      │     │ Sube notebooks al    │     │ Ejecuta jobs en   │
│ sintaxis    │     │ workspace Databricks │     │ producción        │
│ Python      │     │ via CLI              │     │                   │
└─────────────┘     └──────────────────────┘     └───────────────────┘
```

---

## Punto 2 — 3 Conexiones en Databricks (AWS)

Las conexiones se crean desde: **Catalog → ⚙️ → Connections → + Add**

### Conexión 1: GitHub
- **Tipo:** GitHub  
- **Notebook:** `conexiones/03_conexion_github.py`  
- **Para qué sirve:** Git Folders, sincronización de notebooks, CI/CD  
- **Datos que pide:** Personal Access Token (`ghp_...`)  
- **Cómo generar el token:** github.com → Settings → Developer settings → Personal access tokens → Generate new token → marcar `repo` y `workflow`

### Conexión 2: Amazon S3
- **Tipo:** Amazon S3  
- **Notebook:** `conexiones/03_conexion_s3.py`  
- **Para qué sirve:** Leer y escribir archivos (CSV, Parquet, imágenes) en buckets S3  
- **Datos que pide:** AWS Access Key ID + AWS Secret Access Key  
- **Cómo obtenerlos:** AWS Console → IAM → Users → tu usuario → Security credentials → Create access key

### Conexión 3: Amazon RDS (PostgreSQL)
- **Tipo:** PostgreSQL  
- **Notebook:** `conexiones/03_conexion_rds.py`  
- **Para qué sirve:** Leer y escribir datos en base de datos relacional PostgreSQL  
- **Datos que pide:** Host (endpoint RDS), puerto 5432, usuario, contraseña  
- **Cómo crear la RDS:** AWS Console → RDS → Create database → PostgreSQL → Free tier → Public access: Yes → abrir puerto 5432 en Security Group

> Para verificar que están activas: **Catalog → ⚙️ → Connections**  
> Las 3 deben aparecer con estado **Connected**

---

## Punto 3 — Databricks CLI

### Instalación en Windows (Chocolatey)

```powershell
# Instalar Chocolatey si no lo tienes
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Instalar Databricks CLI
choco install databricks-cli

# Verificar instalación
databricks --version
```

### Configurar credenciales

```bash
databricks configure
```

El CLI te pedirá:
```
Databricks Host: https://dbc-8f7207fa-f694.cloud.databricks.com
Databricks Token: dapi...
```

### Comandos principales

```bash
# Ver workspace
databricks workspace list /

# Listar clusters
databricks clusters list

# Subir archivo a un Volume
databricks fs cp mi_imagen.png dbfs:/Volumes/main/s08_storage/archivos_multimedia/

# Listar archivos en el Volume
databricks fs ls /Volumes/main/s08_storage/archivos_multimedia/

# Ver jobs
databricks jobs list

# Ejecutar un job
databricks jobs run-now --job-id <JOB_ID>
```

---

## Punto 4 — Volume en Databricks

### Crear el Volume desde la UI

1. Ve a **Catalog** en el menú lateral
2. Expande tu catálogo (ej. `main`)
3. Clic derecho en un schema → **Create Volume**
4. Nombre: `archivos_multimedia`

### Crear el Volume con SQL

```sql
CREATE SCHEMA IF NOT EXISTS main.s08_storage;

CREATE VOLUME IF NOT EXISTS main.s08_storage.archivos_multimedia
  COMMENT 'Volumen para imágenes y PDFs - S08';
```

### Subir archivos al Volume

**Desde la UI:**
1. **Catalog** → `main` → `s08_storage` → `archivos_multimedia`
2. Clic en **"Upload to this volume"**
3. Arrastra tus imágenes (.png, .jpg) y PDFs (.pdf)

**Desde el CLI:**
```bash
databricks fs cp evidencia_01.png dbfs:/Volumes/main/s08_storage/archivos_multimedia/
databricks fs cp reporte_s08.pdf  dbfs:/Volumes/main/s08_storage/archivos_multimedia/
```

**Desde un notebook:**
```python
# Ruta del volumen
VOLUME_PATH = "/Volumes/main/s08_storage/archivos_multimedia"

# Listar archivos
files = dbutils.fs.ls(VOLUME_PATH)
for f in files:
    print(f.name, f.size)
```

---

## Cómo subir este proyecto a GitHub

```bash
# 1. Inicializar repositorio git
git init
git add .
git commit -m "feat: S08 AP4 - Databricks e Integraciones"

# 2. Crear repo en GitHub (github.com → New repository)
#    Nombre: github-databricks
#    Visibilidad: Public

# 3. Conectar y subir
git remote add origin https://github.com/TU_USUARIO/github-databricks.git
git branch -M main
git push -u origin main
```

Después del push, el pipeline de GitHub Actions se ejecutará automáticamente.  
Puedes verlo en: **tu-repo → Actions**

---

## Notebooks incluidos

| Archivo | Descripción |
|---------|-------------|
| `notebooks/01_exploracion_datos.py` | Crea un DataFrame con datos de ejemplo, análisis exploratorio y guarda en Delta Lake |
| `notebooks/02_transformaciones.py` | Transforma los datos: clasifica salarios, agrega columnas calculadas, filtra |
| `conexiones/03_conexion_github.py` | Configura la conexión GitHub, verifica Git Folder y hace pull desde la API |
| `conexiones/03_conexion_s3.py` | Conecta con Amazon S3: lista bucket, lee y escribe CSV y Parquet |
| `conexiones/03_conexion_rds.py` | Conecta con Amazon RDS PostgreSQL: escribe y lee tablas via JDBC |
| `volumen/04_volumen_archivos.py` | Crea el Volume, sube archivos y registra en tabla del catálogo |
