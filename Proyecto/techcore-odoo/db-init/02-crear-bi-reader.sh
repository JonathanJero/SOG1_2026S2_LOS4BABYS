#!/bin/bash
set -e

echo "=================================================="
echo " [TechCore] Configurando vistas de Business Intelligence"
echo "=================================================="

SQL_FILE="/docker-entrypoint-initdb.d/vistas_bi.sql"
if [ -f "$SQL_FILE" ]; then
    echo "Aplicando vistas BI y permisos para bi_reader..."
    psql --username "$POSTGRES_USER" --dbname "TechCore_DB" --file "$SQL_FILE" --quiet
    echo "[OK] Rol bi_reader y vistas analiticas configurados correctamente."
else
    echo "[WARN] No se encontro $SQL_FILE en /docker-entrypoint-initdb.d/"
fi
