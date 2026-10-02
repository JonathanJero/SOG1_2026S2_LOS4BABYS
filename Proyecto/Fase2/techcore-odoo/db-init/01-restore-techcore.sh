#!/bin/bash
set -e

echo "=================================================="
echo " [TechCore] Iniciando aprovisionamiento automático"
echo "=================================================="

# 1. Crear la base de datos TechCore_DB si no existe
echo "1. Creando base de datos TechCore_DB..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    SELECT 'CREATE DATABASE "TechCore_DB" OWNER "$POSTGRES_USER"'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'TechCore_DB')\gexec
    GRANT ALL PRIVILEGES ON DATABASE "TechCore_DB" TO "$POSTGRES_USER";
EOSQL

# 2. Restaurar la información desde el dump comprimido o sql
echo "2. Restaurando esquema y datos para TechCore_DB..."
if [ -f /docker-entrypoint-initdb.d/dump.sql.gz ]; then
    echo "Restaurando desde dump.sql.gz..."
    gunzip -c /docker-entrypoint-initdb.d/dump.sql.gz | psql --username "$POSTGRES_USER" --dbname "TechCore_DB" --quiet
elif [ -f /docker-entrypoint-initdb.d/dump.sql ]; then
    echo "Restaurando desde dump.sql..."
    psql --username "$POSTGRES_USER" --dbname "TechCore_DB" --quiet < /docker-entrypoint-initdb.d/dump.sql
else
    echo "ADVERTENCIA: No se encontró dump en /docker-entrypoint-initdb.d/"
fi

echo "=================================================="
echo " [TechCore] Base de datos TechCore_DB restaurada con éxito"
echo "=================================================="
