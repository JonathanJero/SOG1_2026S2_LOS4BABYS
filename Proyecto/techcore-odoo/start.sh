#!/bin/bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

echo "=========================================================="
echo " TechCore Solutions Guatemala - Odoo 17 ERP/CRM"
echo "=========================================================="

# 1. Asegurar permisos en filestore y db-init
echo "[INFO] Configurando permisos locales..."
chmod -R a+rwX filestore db-init scripts 2>/dev/null || true
chmod +x db-init/01-restore-techcore.sh db-init/02-crear-bi-reader.sh 2>/dev/null || true

# 1b. Normalizar finales de linea (un checkout con CRLF deja el shebang como
#     "#!/bin/bash\r" y PostgreSQL no puede ejecutar los scripts de init)
sed -i 's/\r$//' db-init/*.sh 2>/dev/null || true

# 2. Levantar contenedores
echo "[INFO] Levantando servicios con Docker Compose..."
docker compose up -d

echo ""
echo "[WAIT] Esperando inicializacion de la Base de Datos y Odoo..."
echo "       (En el primer arranque se restaurara automaticamente TechCore_DB)"

# Esperar a que la base de datos este lista.
# -h 127.0.0.1 fuerza TCP: durante la restauracion inicial el servidor
# temporal de PostgreSQL solo escucha en el socket unix y un pg_isready por
# socket respondia "listo" antes de terminar el restore.
MAX_WAIT=180
COUNT=0
DB_READY=1
until docker compose exec -T db pg_isready -h 127.0.0.1 -U odoo -d TechCore_DB >/dev/null 2>&1; do
    if [ $COUNT -ge $MAX_WAIT ]; then
        DB_READY=0
        break
    fi
    sleep 2
    COUNT=$((COUNT+2))
    printf "."
done

echo ""
if [ "$DB_READY" -eq 1 ] && ! docker compose exec -T db psql -h 127.0.0.1 -U odoo -d TechCore_DB \
    -v ON_ERROR_STOP=1 -tAc "SELECT count(*) FROM ir_module_module" >/dev/null 2>&1; then
    DB_READY=0
fi

if [ "$DB_READY" -eq 0 ]; then
    echo "[WARN] Tiempo de espera excedido o la base no quedo restaurada."
    echo "       Revisa los logs con: docker compose logs db"
    SKIP_MENU_FIX=1
else
    echo "[OK] Base de datos TechCore_DB lista y conectada."
fi

# 4. Esperar a que Odoo responda por HTTP (evita competir con la carga del
# registro durante el primer arranque). Solo si curl esta disponible.
if [ -z "$SKIP_MENU_FIX" ] && command -v curl >/dev/null 2>&1; then
    echo ""
    echo "[WAIT] Esperando a que Odoo responda en http://localhost:8069 ..."
    ODOO_WAIT=0
    until curl -fsS -o /dev/null --max-time 5 http://localhost:8069/web/login 2>/dev/null; do
        if [ $ODOO_WAIT -ge 90 ]; then
            echo "[WARN] Odoo aun no responde por HTTP. Se continua con el resto de verificaciones."
            break
        fi
        sleep 3
        ODOO_WAIT=$((ODOO_WAIT+3))
        printf "."
    done
    echo ""
fi

# 5. Reparar el menu de Ventas
# El snapshot original se creo sin el modulo 'sale' instalado, por lo que el
# menu raiz de Ventas quedo archivado en el dump. Este paso lo desarchiva de
# forma idempotente en cada arranque, para que la app quede disponible sin
# importar con que respaldo se restauro la base.
if [ -z "$SKIP_MENU_FIX" ]; then
    echo ""
    echo "[INFO] Verificando disponibilidad del menu de Ventas..."
    MENU_LOG="$(mktemp)"
    if docker compose run --rm -T web odoo shell \
        -c /etc/odoo/odoo.conf \
        -d TechCore_DB \
        --db_host=db \
        --stop-after-init \
        --log-level=warn \
        < scripts/activar_menu_ventas.py >"$MENU_LOG" 2>&1; then
        grep -E "\[(OK|FIX|WARN)\]" "$MENU_LOG" || true
        echo "[OK] Menu de Ventas verificado."
    else
        grep -E "\[(OK|FIX|WARN)\]" "$MENU_LOG" || true
        echo "[WARN] No se pudo verificar el menu de Ventas. Si no aparece la app"
        echo "       Ventas, revisa: docker compose logs web"
    fi
    rm -f "$MENU_LOG"
fi

# 6. Asegurar rol y vistas de Business Intelligence
if [ -z "$SKIP_MENU_FIX" ]; then
    echo ""
    echo "[INFO] Verificando vistas analiticas y usuario bi_reader..."
    if docker compose exec -T db psql -U odoo -d TechCore_DB \
        -v ON_ERROR_STOP=1 -f /docker-entrypoint-initdb.d/sql/vistas_bi.sql >/dev/null 2>&1; then
        echo "[OK] Vistas de Business Intelligence verificadas."
    else
        echo "[WARN] No se pudieron aplicar las vistas BI automaticamente."
    fi
fi

echo ""
echo "=========================================================="
echo " [OK] ENTORNO LISTO Y OPERATIVO"
echo "=========================================================="
echo " Acceso Web Odoo: http://localhost:8069"
echo " Base de Datos:   TechCore_DB"
echo " Usuario Admin:   admin@techcore.gt"
echo " Contrasena:      1234"
echo " Master Pwd:      techcore_master_pwd"
echo "----------------------------------------------------------"
echo " Conexion Power BI Desktop / BI Analytics:"
echo " Servidor / Host: localhost:5432"
echo " Base de Datos:   TechCore_DB"
echo " Usuario BI:      bi_reader"
echo " Contrasena BI:   bi_reader_techcore"
echo " Vistas:          v_bi_ventas_detalle, v_bi_inventario,"
echo "                  v_bi_top_productos, v_bi_compras"
echo "=========================================================="
echo " Comandos utiles:"
echo "   - Ver logs:    docker compose logs -f"
echo "   - Detener:     docker compose down"
echo "   - Reiniciar:   docker compose restart"
echo "=========================================================="
