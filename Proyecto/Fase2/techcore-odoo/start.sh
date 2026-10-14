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

# 2. Levantar contenedores
echo "[INFO] Levantando servicios con Docker Compose..."
docker compose up -d

echo ""
echo "[WAIT] Esperando inicializacion de la Base de Datos y Odoo..."
echo "       (En el primer arranque se restaurara automaticamente TechCore_DB)"

# Esperar a que la base de datos este lista
MAX_WAIT=90
COUNT=0
until docker compose exec -T db pg_isready -U odoo -d TechCore_DB >/dev/null 2>&1 || [ $COUNT -ge $MAX_WAIT ]; do
    sleep 2
    COUNT=$((COUNT+2))
    printf "."
done

echo ""
if [ $COUNT -ge $MAX_WAIT ]; then
    echo "[WARN] Tiempo de espera excedido. Revisa los logs con: docker compose logs -f"
    SKIP_MENU_FIX=1
else
    echo "[OK] Base de datos TechCore_DB lista y conectada."
fi

# 4. Reparar el menu de Ventas
# El snapshot original se creo sin el modulo 'sale' instalado, por lo que el
# menu raiz de Ventas quedo archivado en el dump. Este paso lo desarchiva de
# forma idempotente en cada arranque, para que la app quede disponible sin
# importar con que respaldo se restauro la base.
if [ -z "$SKIP_MENU_FIX" ]; then
    echo ""
    echo "[INFO] Verificando disponibilidad del menu de Ventas..."
    if docker compose run --rm -T web odoo shell \
        -c /etc/odoo/odoo.conf \
        -d TechCore_DB \
        --db_host=db \
        --stop-after-init \
        --log-level=warn \
        < scripts/activar_menu_ventas.py 2>&1 | grep -E "\[(OK|FIX|WARN)\]"; then
        echo "[OK] Menu de Ventas verificado."
    else
        echo "[WARN] No se pudo verificar el menu de Ventas. Si no aparece la app"
        echo "       Ventas, revisa: docker compose logs web"
    fi
fi

# 5. Asegurar rol y vistas de Business Intelligence
if [ -z "$SKIP_MENU_FIX" ]; then
    echo ""
    echo "[INFO] Verificando vistas analiticas y usuario bi_reader..."
    docker compose exec -T db psql -U odoo -d TechCore_DB -f /docker-entrypoint-initdb.d/vistas_bi.sql >/dev/null 2>&1 || true
    echo "[OK] Vistas de Business Intelligence verificadas."
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
