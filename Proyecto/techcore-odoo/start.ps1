# ==============================================================================
# TechCore Solutions Guatemala - Odoo 17 ERP/CRM (Windows PowerShell)
# ==============================================================================
# Notas de compatibilidad con Windows PowerShell 5.1:
#   * Con $ErrorActionPreference = "Stop", cualquier comando nativo que escriba
#     en stderr (docker compose lo hace constantemente) se convierte en un error
#     terminante. Por eso aqui se usa "Continue" y se revisa $LASTEXITCODE.
#   * La comprobacion de readiness usa TCP (-h 127.0.0.1). pg_isready por socket
#     unix responde "aceptando conexiones" durante la restauracion inicial.
# ==============================================================================
$ErrorActionPreference = "Continue"

try {
    # UTF-8 sin BOM: [Text.Encoding]::UTF8 agrega BOM y al pipear el script de
    # Odoo shell provoca "SyntaxError: invalid non-printable character U+FEFF".
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [Console]::OutputEncoding = $utf8NoBom
    $OutputEncoding = $utf8NoBom
} catch { }

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

function Write-Ok($Message) { Write-Host $Message -ForegroundColor Green }
function Write-Info($Message) { Write-Host $Message -ForegroundColor Yellow }
function Write-Detail($Message) { Write-Host $Message -ForegroundColor DarkGray }

function Invoke-Capture {
    # Ejecuta un comando nativo capturando stdout y stderr como texto plano.
    param([scriptblock]$Command)
    $lines = & $Command 2>&1 | ForEach-Object { "$_" }
    return [pscustomobject]@{
        ExitCode = $LASTEXITCODE
        Lines    = @($lines)
    }
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " TechCore Solutions Guatemala - Odoo 17 ERP/CRM" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Comprobar que Docker este instalado y en ejecucion
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] No se encontro el comando 'docker'. Instale Docker Desktop." -ForegroundColor Red
    exit 1
}

$dockerInfo = Invoke-Capture { docker info }
if ($dockerInfo.ExitCode -ne 0) {
    Write-Host "[ERROR] Docker Desktop no esta en ejecucion. Por favor inicie Docker Desktop y vuelva a intentar." -ForegroundColor Red
    exit 1
}

# 2. Normalizar finales de linea de los scripts de inicializacion.
# Git en Windows puede hacer checkout con CRLF; el shebang queda como
# "#!/bin/bash\r" y el entrypoint de PostgreSQL falla con:
#   "cannot execute: required file not found"
$shellScripts = @(Get-ChildItem "db-init/*.sh" -ErrorAction SilentlyContinue)
foreach ($file in $shellScripts) {
    $text = [System.IO.File]::ReadAllText($file.FullName)
    $normalized = ($text -replace "`r`n", "`n") -replace "`r", "`n"
    if ($normalized -ne $text) {
        [System.IO.File]::WriteAllText($file.FullName, $normalized, (New-Object System.Text.UTF8Encoding($false)))
        Write-Detail "[FIX] Finales de linea convertidos a LF: $($file.Name)"
    }
}

# 3. Levantar contenedores con Docker Compose
Write-Info "[INFO] Levantando servicios con Docker Compose..."
$up = Invoke-Capture { docker compose up -d }
if ($up.ExitCode -ne 0) {
    $up.Lines | ForEach-Object { Write-Host "       $_" -ForegroundColor DarkGray }
    Write-Host "[ERROR] No se pudieron levantar los contenedores." -ForegroundColor Red
    Write-Host "        Revise los logs con: docker compose logs" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Info "[WAIT] Esperando inicializacion de la Base de Datos y Odoo..."
Write-Host "       (En el primer arranque se restaurara automaticamente TechCore_DB)" -ForegroundColor Gray

# 3. Esperar a que PostgreSQL acepte conexiones TCP Y la base este restaurada
#    (durante el restore inicial el servidor temporal no abre TCP).
$MaxWait = 180
$Elapsed = 0
$DbReady = $false

while ($Elapsed -lt $MaxWait) {
    $ping = Invoke-Capture { docker compose exec -T db pg_isready -h 127.0.0.1 -U odoo -d TechCore_DB }
    if ($ping.ExitCode -eq 0) {
        $DbReady = $true
        break
    }
    Start-Sleep -Seconds 2
    $Elapsed += 2
    Write-Host -NoNewline "."
}

Write-Host ""
if ($DbReady) {
    # Verificacion final: la base debe tener contenido (modulos de Odoo).
    $count = Invoke-Capture { docker compose exec -T db psql -h 127.0.0.1 -U odoo -d TechCore_DB -v ON_ERROR_STOP=1 -tAc "SELECT count(*) FROM ir_module_module" }
    $modules = ($count.Lines | Where-Object { $_ -match '^\s*\d+\s*$' } | Select-Object -Last 1)
    if ($count.ExitCode -ne 0 -or -not $modules -or [int]$modules -le 0) {
        $DbReady = $false
    }
}

if (-not $DbReady) {
    Write-Host "[WARN] Tiempo de espera excedido o la base no quedo restaurada." -ForegroundColor Yellow
    Write-Host "       Revise los logs con: docker compose logs db" -ForegroundColor Yellow
    $dbState = Invoke-Capture { docker compose ps db }
    $dbState.Lines | ForEach-Object { Write-Host "       $_" -ForegroundColor DarkGray }
} else {
    Write-Ok "[OK] Base de datos TechCore_DB lista y conectada."
}

# 4. Esperar a que Odoo responda por HTTP. Hacerlo antes de reparar el menu
#    evita competir con la carga del registro de Odoo durante el primer arranque.
$OdooReady = $false
$HttpElapsed = 0
$HttpMaxWait = 90

if ($DbReady) {
    Write-Host ""
    Write-Info "[WAIT] Esperando a que Odoo responda en http://localhost:8069 ..."
    while ($HttpElapsed -lt $HttpMaxWait) {
        try {
            $request = [System.Net.WebRequest]::Create("http://localhost:8069/web/login")
            $request.Proxy = $null
            $request.Timeout = 5000
            $response = $request.GetResponse()
            $statusCode = [int]$response.StatusCode
            $response.Close()
            if ($statusCode -ge 200 -and $statusCode -lt 500) {
                $OdooReady = $true
                break
            }
        } catch { }

        Start-Sleep -Seconds 3
        $HttpElapsed += 3
        Write-Host -NoNewline "."
    }
    Write-Host ""
}

# 5. Reparar el menu de Ventas
Write-Host ""
Write-Info "[INFO] Verificando disponibilidad del menu de Ventas..."
if (-not $DbReady) {
    Write-Host "[WARN] Se omite la verificacion del menu porque PostgreSQL no esta listo." -ForegroundColor Yellow
} else {
    if (-not (Test-Path "scripts/activar_menu_ventas.py")) {
        Write-Host "[WARN] No se encontro scripts/activar_menu_ventas.py." -ForegroundColor Yellow
    } else {
        $MenuReady = $false
        $MaxMenuAttempts = 15

        for ($Attempt = 1; $Attempt -le $MaxMenuAttempts; $Attempt++) {
            $menu = Invoke-Capture {
                Get-Content -Raw "scripts/activar_menu_ventas.py" | docker compose run --rm -T web odoo shell `
                    -c /etc/odoo/odoo.conf `
                    -d TechCore_DB `
                    --db_host=db `
                    --stop-after-init `
                    --log-level=warn
            }

            $menu.Lines |
                Where-Object { $_ -match '\[(OK|FIX|WARN)\]' } |
                ForEach-Object { Write-Detail "       $_" }

            if ($menu.ExitCode -eq 0) {
                $MenuReady = $true
                break
            }

            if ($Attempt -lt $MaxMenuAttempts) {
                Write-Host "[WAIT] Odoo aun no esta disponible (intento $Attempt/$MaxMenuAttempts)." -ForegroundColor Gray
                Start-Sleep -Seconds 2
            }
        }

        if ($MenuReady) {
            Write-Ok "[OK] Menu de Ventas verificado."
        } else {
            Write-Host "[WARN] No se pudo verificar el menu de Ventas automaticamente." -ForegroundColor Yellow
            $menu.Lines | Select-Object -Last 10 | ForEach-Object { Write-Host "       $_" -ForegroundColor DarkGray }
        }
    }
}

# 6. Asegurar rol y vistas de Business Intelligence
Write-Host ""
Write-Info "[INFO] Verificando vistas analiticas y usuario bi_reader..."
if (-not $DbReady) {
    Write-Host "[WARN] Se omiten las vistas BI porque PostgreSQL no esta listo." -ForegroundColor Yellow
} else {
    $bi = Invoke-Capture { docker compose exec -T db psql -U odoo -d TechCore_DB -v ON_ERROR_STOP=1 -f /docker-entrypoint-initdb.d/sql/vistas_bi.sql }
    if ($bi.ExitCode -eq 0) {
        Write-Ok "[OK] Vistas de Business Intelligence verificadas."
    } else {
        Write-Host "[WARN] No se pudieron aplicar las vistas BI automaticamente." -ForegroundColor Yellow
        $bi.Lines | Select-Object -Last 10 | ForEach-Object { Write-Host "       $_" -ForegroundColor DarkGray }
    }
}

# 7. Banner final de acceso
Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
if ($DbReady -and $OdooReady) {
    Write-Host " [OK] ENTORNO LISTO Y OPERATIVO" -ForegroundColor Green
} elseif ($DbReady) {
    Write-Host " [WARN] BASE DE DATOS LISTA, ODOO AUN INICIANDO" -ForegroundColor Yellow
    Write-Host "        Abra http://localhost:8069 en unos segundos." -ForegroundColor Yellow
    Write-Host "        Si no responde: docker compose logs web" -ForegroundColor Yellow
} else {
    Write-Host " [WARN] ENTORNO INCOMPLETO" -ForegroundColor Yellow
    Write-Host "        Revise: docker compose logs db" -ForegroundColor Yellow
}
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

if (-not $DbReady) { exit 1 }
