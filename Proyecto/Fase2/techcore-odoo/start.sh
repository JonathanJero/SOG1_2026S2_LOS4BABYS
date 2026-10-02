#!/bin/bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

echo "=========================================================="
echo " TechCore Solutions Guatemala - Odoo 17 ERP/CRM"
echo "=========================================================="

# 1. Asegurar permisos en filestore y db-init
echo "[INFO] Configurando permisos locales..."
chmod -R a+rwX filestore db-init 2>/dev/null || true
chmod +x db-init/01-restore-techcore.sh 2>/dev/null || true

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
else
    echo "[OK] Base de datos TechCore_DB lista y conectada."
fi

echo ""
echo "=========================================================="
echo " [OK] ENTORNO LISTO Y OPERATIVO"
echo "=========================================================="
echo " Acceso Web:     http://localhost:8069"
echo " Base de Datos:  TechCore_DB"
echo " Usuario Admin:  admin@techcore.gt"
echo " Password Admin: admin (o techcore_secure_pwd)"
echo " Master Pwd:     techcore_master_pwd"
echo "=========================================================="
echo " Comandos utiles:"
echo "   - Ver logs:   docker compose logs -f"
echo "   - Detener:    docker compose down"
echo "   - Reiniciar:  docker compose restart"
echo "=========================================================="
