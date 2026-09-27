# ==========================================================
# DATABRICKS CLI - Guía Windows (PowerShell)
# Sesión 08 | AP4 | Juan Gabriel Condori Jara
# ==========================================================

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  DATABRICKS CLI - WINDOWS POWERSHELL" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# ----------------------------------------------------------
# PASO 1: INSTALAR CON CHOCOLATEY
# ----------------------------------------------------------
Write-Host ""
Write-Host "--- PASO 1: INSTALAR DATABRICKS CLI ---" -ForegroundColor Yellow
Write-Host ""
Write-Host "Opcion A - Chocolatey (recomendado):" -ForegroundColor Green
Write-Host "  choco install databricks-cli"
Write-Host ""
Write-Host "Opcion B - WinGet:" -ForegroundColor Green
Write-Host "  winget install Databricks.DatabricksCLI"
Write-Host ""
Write-Host "Opcion C - Descarga directa:" -ForegroundColor Green
Write-Host "  https://github.com/databricks/cli/releases/latest"

# ----------------------------------------------------------
# PASO 2: VERIFICAR VERSION
# ----------------------------------------------------------
Write-Host ""
Write-Host "--- PASO 2: VERIFICAR VERSION ---" -ForegroundColor Yellow
try {
    $version = & databricks --version 2>&1
    Write-Host "Version instalada: $version" -ForegroundColor Green
} catch {
    Write-Host "Databricks CLI no instalado. Instalar primero." -ForegroundColor Red
}

# ----------------------------------------------------------
# PASO 3: CONFIGURAR CREDENCIALES
# ----------------------------------------------------------
Write-Host ""
Write-Host "--- PASO 3: CONFIGURAR CREDENCIALES ---" -ForegroundColor Yellow
Write-Host ""
Write-Host "Ejecuta en tu terminal:" -ForegroundColor White
Write-Host "  databricks configure" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ingresa cuando te pida:" -ForegroundColor White
Write-Host "  Host:  https://dbc-XXXXXXXX-XXXX.cloud.databricks.com" -ForegroundColor Gray
Write-Host "  Token: dapi... (generado en Settings > Developer > Access Tokens)" -ForegroundColor Gray

# ----------------------------------------------------------
# PASO 4: COMANDOS DEMOSTRACIÓN
# ----------------------------------------------------------
Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  COMANDOS PRINCIPALES" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

$comandos = @(
    @{ desc = "Ver workspace raiz";           cmd = "databricks workspace list /" },
    @{ desc = "Listar clusters";              cmd = "databricks clusters list" },
    @{ desc = "Listar jobs";                  cmd = "databricks jobs list" },
    @{ desc = "Subir archivo a Volume";       cmd = "databricks fs cp imagen.png dbfs:/Volumes/main/s08_storage/archivos_multimedia/" },
    @{ desc = "Listar archivos en Volume";    cmd = "databricks fs ls /Volumes/main/s08_storage/archivos_multimedia/" },
    @{ desc = "Ver secretos";                 cmd = "databricks secrets list-scopes" },
    @{ desc = "Ejecutar un Job";              cmd = "databricks jobs run-now --job-id <JOB_ID>" }
)

foreach ($item in $comandos) {
    Write-Host ""
    Write-Host "# $($item.desc)" -ForegroundColor Yellow
    Write-Host "  $($item.cmd)" -ForegroundColor White
}

# ----------------------------------------------------------
# PASO 5: EJECUCION REAL
# ----------------------------------------------------------
Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  DEMOSTRACION EN VIVO" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "1) Verificando conexion..." -ForegroundColor Yellow
try {
    $result = & databricks workspace list / 2>&1
    Write-Host $result -ForegroundColor Green
} catch {
    Write-Host "   Configura las credenciales con: databricks configure" -ForegroundColor Red
}

Write-Host ""
Write-Host "2) Listando clusters..." -ForegroundColor Yellow
try {
    $clusters = & databricks clusters list 2>&1
    Write-Host $clusters -ForegroundColor Green
} catch {
    Write-Host "   Configura las credenciales primero." -ForegroundColor Red
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host "  OK DEMO COMPLETADA" -ForegroundColor Green
Write-Host "  Estudiante: Juan Gabriel Condori Jara" -ForegroundColor Green
Write-Host "  Sesion: S08 AP4 - Databricks e Integraciones" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
