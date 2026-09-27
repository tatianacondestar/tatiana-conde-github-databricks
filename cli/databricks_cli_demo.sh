#!/bin/bash
# ==========================================================
# DATABRICKS CLI - Guía de instalación y uso
# Sesión 08 | AP4 | Juan Gabriel Condori Jara
# ==========================================================

echo "=================================================="
echo "  DATABRICKS CLI - INSTALACIÓN Y CONFIGURACIÓN"
echo "=================================================="

# ----------------------------------------------------------
# PASO 1: INSTALACIÓN
# ----------------------------------------------------------
echo ""
echo "--- PASO 1: INSTALAR DATABRICKS CLI ---"
echo ""

# Opción A: Con Chocolatey (Windows)
echo "[Windows - Chocolatey]"
echo "  choco install databricks-cli"

# Opción B: Con curl (Linux/Mac)
echo ""
echo "[Linux / Mac - curl]"
echo "  curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh"

# Opción C: Con pip (Python)
echo ""
echo "[Python - pip]"
echo "  pip install databricks-cli"

# ----------------------------------------------------------
# PASO 2: VERIFICAR INSTALACIÓN
# ----------------------------------------------------------
echo ""
echo "--- PASO 2: VERIFICAR VERSIÓN ---"
databricks --version
# Salida esperada: Databricks CLI v0.x.x

# ----------------------------------------------------------
# PASO 3: CONFIGURAR CREDENCIALES
# ----------------------------------------------------------
echo ""
echo "--- PASO 3: CONFIGURAR CREDENCIALES ---"
echo "Ejecuta: databricks configure"
echo ""
echo "Te pedirá:"
echo "  Databricks Host: https://dbc-XXXXXXXX-XXXX.cloud.databricks.com"
echo "  Databricks Token: dapi..."
echo ""
echo "El token se genera en:"
echo "  Databricks UI → Settings → Developer → Access Tokens → Generate new token"

# Si se ejecuta el script con las variables de entorno seteadas:
if [ -n "$DATABRICKS_HOST" ] && [ -n "$DATABRICKS_TOKEN" ]; then
  echo ""
  echo "Configurando con variables de entorno..."
  databricks configure --token <<EOF
$DATABRICKS_HOST
$DATABRICKS_TOKEN
EOF
  echo "Configuración completada."
fi

# ----------------------------------------------------------
# PASO 4: COMANDOS ÚTILES
# ----------------------------------------------------------
echo ""
echo "=================================================="
echo "  COMANDOS ÚTILES DEL CLI"
echo "=================================================="

echo ""
echo "# Ver información del workspace"
echo "databricks workspace list /"

echo ""
echo "# Listar clusters disponibles"
echo "databricks clusters list"

echo ""
echo "# Ver jobs configurados"
echo "databricks jobs list"

echo ""
echo "# Subir un archivo al workspace"
echo "databricks workspace import archivo.py /Users/juan.condori/archivo"

echo ""
echo "# Subir archivo a un Volume"
echo "databricks fs cp imagen.png dbfs:/Volumes/main/s08_storage/archivos_multimedia/"

echo ""
echo "# Listar archivos en un Volume"
echo "databricks fs ls /Volumes/main/s08_storage/archivos_multimedia/"

echo ""
echo "# Ejecutar un job"
echo "databricks jobs run-now --job-id <JOB_ID>"

echo ""
echo "# Ver secretos"
echo "databricks secrets list-scopes"

# ----------------------------------------------------------
# PASO 5: EJECUTAR COMANDOS REALES (si hay credenciales)
# ----------------------------------------------------------
echo ""
echo "=================================================="
echo "  DEMOSTRACIÓN EN VIVO"
echo "=================================================="

echo ""
echo "1) Verificando conexión con workspace..."
databricks workspace list / 2>/dev/null || echo "   (configura las credenciales primero)"

echo ""
echo "2) Listando clusters..."
databricks clusters list 2>/dev/null || echo "   (configura las credenciales primero)"

echo ""
echo "3) Listando jobs..."
databricks jobs list 2>/dev/null || echo "   (configura las credenciales primero)"

echo ""
echo "=================================================="
echo "  ✅ DEMO COMPLETADA"
echo "  Estudiante: Juan Gabriel Condori Jara"
echo "  Sesión: S08 AP4 - Databricks e Integraciones"
echo "=================================================="
