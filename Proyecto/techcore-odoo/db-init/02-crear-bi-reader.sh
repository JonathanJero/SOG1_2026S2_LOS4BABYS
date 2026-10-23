#!/bin/bash
set -e

echo "=================================================="
echo " [TechCore] Configurando vistas de Business Intelligence"
echo "=================================================="

SQL_FILE="/docker-entrypoint-initdb.d/sql/vistas_bi.sql"
if [ -f "$SQL_FILE" ]; then
    echo "Aplicando vistas BI y permisos para bi_reader..."
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "TechCore_DB" --file "$SQL_FILE" --quiet
    echo "[OK] Rol bi_reader y vistas analiticas configurados correctamente."
else
    echo "[WARN] No se encontro $SQL_FILE en /docker-entrypoint-initdb.d/"
fi
