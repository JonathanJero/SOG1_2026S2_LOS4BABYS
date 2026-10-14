# ==============================================================================
# TechCore Solutions Guatemala - Odoo 17 ERP/CRM (Windows PowerShell)
# ==============================================================================
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " TechCore Solutions Guatemala - Odoo 17 ERP/CRM" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Comprobar que Docker este en ejecucion
try {
    docker info > $null 2>&1
} catch {
    Write-Host "[ERROR] Docker Desktop no esta en ejecucion. Por favor inicie Docker Desktop y vuelva a intentar." -ForegroundColor Red
    exit 1
}

# 2. Levantar contenedores con Docker Compose
Write-Host "[INFO] Levantando servicios con Docker Compose..." -ForegroundColor Yellow
docker compose up -d

Write-Host ""
Write-Host "[WAIT] Esperando inicializacion de la Base de Datos y Odoo..." -ForegroundColor Yellow
Write-Host "       (En el primer arranque se restaurara automaticamente TechCore_DB)" -ForegroundColor Gray

# 3. Esperar a que PostgreSQL este listo
$MaxWait = 90
$Elapsed = 0
$DbReady = $false

while ($Elapsed -lt $MaxWait) {
    $check = docker compose exec -T db pg_isready -U odoo -d TechCore_DB 2>&1
    if ($LASTEXITCODE -eq 0) {
        $DbReady = $true
        break
    }
    Start-Sleep -Seconds 2
    $Elapsed += 2
    Write-Host -NoNewline "."
}

Write-Host ""
if (-not $DbReady) {
    Write-Host "[WARN] Tiempo de espera excedido. Revisa los logs con: docker compose logs -f" -ForegroundColor Yellow
} else {
    Write-Host "[OK] Base de datos TechCore_DB lista y conectada." -ForegroundColor Green
}

# 4. Reparar el menu de Ventas
Write-Host ""
Write-Host "[INFO] Verificando disponibilidad del menu de Ventas..." -ForegroundColor Yellow
try {
    Get-Content "scripts/activar_menu_ventas.py" | docker compose run --rm -T web odoo shell `
        -c /etc/odoo/odoo.conf `
        -d TechCore_DB `
        --db_host=db `
        --stop-after-init `
        --log-level=warn
    Write-Host "[OK] Menu de Ventas verificado." -ForegroundColor Green
} catch {
    Write-Host "[WARN] No se pudo verificar el menu de Ventas automaticamente." -ForegroundColor Yellow
}

# 5. Asegurar rol y vistas de Business Intelligence
Write-Host ""
Write-Host "[INFO] Verificando vistas analiticas y usuario bi_reader..." -ForegroundColor Yellow
try {
    docker compose exec -T db psql -U odoo -d TechCore_DB -f /docker-entrypoint-initdb.d/vistas_bi.sql > $null 2>&1
    Write-Host "[OK] Vistas de Business Intelligence verificadas." -ForegroundColor Green
} catch {
    Write-Host "[WARN] No se pudieron aplicar las vistas BI automaticamente." -ForegroundColor Yellow
}

# 6. Banner final de acceso
Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " [OK] ENTORNO LISTO Y OPERATIVO" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Acceso Web Odoo: http://localhost:8069" -ForegroundColor White
Write-Host " Base de Datos:   TechCore_DB" -ForegroundColor White
Write-Host " Usuario Admin:   admin@techcore.gt" -ForegroundColor White
Write-Host " Contrasena:      1234" -ForegroundColor White
Write-Host " Master Pwd:      techcore_master_pwd" -ForegroundColor White
Write-Host "----------------------------------------------------------" -ForegroundColor DarkGray
Write-Host " Conexion Power BI Desktop / BI Analytics:" -ForegroundColor Magenta
Write-Host " Servidor / Host: localhost:5432" -ForegroundColor White
Write-Host " Base de Datos:   TechCore_DB" -ForegroundColor White
Write-Host " Usuario BI:      bi_reader" -ForegroundColor White
Write-Host " Contrasena BI:   bi_reader_techcore" -ForegroundColor White
Write-Host " Vistas:          v_bi_ventas_detalle, v_bi_inventario," -ForegroundColor White
Write-Host "                  v_bi_top_productos, v_bi_compras" -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Comandos utiles:" -ForegroundColor Gray
Write-Host "   - Ver logs:    docker compose logs -f" -ForegroundColor Gray
Write-Host "   - Detener:     docker compose down" -ForegroundColor Gray
Write-Host "   - Reiniciar:   docker compose restart" -ForegroundColor Gray
Write-Host "==========================================================" -ForegroundColor Cyan
