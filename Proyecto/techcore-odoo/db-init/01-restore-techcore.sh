#!/bin/bash
set -Eeuo pipefail

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

# 2. Crear el rol bi_reader ANTES de restaurar.
# El dump incluye las sentencias GRANT ... TO bi_reader (ACL del esquema public
# y de las vistas BI). Si el rol no existe todavía, la restauración falla con
# "role bi_reader does not exist", el entrypoint de PostgreSQL aborta y el
# contenedor se reinicia dejando la base a medio configurar.
echo "2. Asegurando rol de Business Intelligence bi_reader..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'bi_reader') THEN
            CREATE ROLE bi_reader WITH LOGIN PASSWORD 'bi_reader_techcore';
        END IF;
    END
    \$\$;
EOSQL

# 3. Restaurar la información desde el dump comprimido o sql.
# El dump vive en db-init/sql/ para que el entrypoint oficial de PostgreSQL no
# lo ejecute por su cuenta (solo procesa los archivos del primer nivel). Si
# estuviera en db-init/, se restauraría una segunda vez sobre la base "postgres".
DUMP_DIR="/docker-entrypoint-initdb.d/sql"
echo "3. Restaurando esquema y datos para TechCore_DB..."
if [ -f "$DUMP_DIR/dump.sql.gz" ]; then
    echo "Restaurando desde $DUMP_DIR/dump.sql.gz..."
    gunzip -c "$DUMP_DIR/dump.sql.gz" | psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "TechCore_DB" --quiet
elif [ -f "$DUMP_DIR/dump.sql" ]; then
    echo "Restaurando desde $DUMP_DIR/dump.sql..."
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "TechCore_DB" --quiet < "$DUMP_DIR/dump.sql"
else
    echo "ERROR: No se encontró dump en $DUMP_DIR/" >&2
    exit 1
fi

echo "=================================================="
echo " [TechCore] Base de datos TechCore_DB restaurada con éxito"
echo "=================================================="
