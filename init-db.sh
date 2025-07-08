#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER app_user WITH PASSWORD 'app_password';
    \connect postgres
    CREATE DATABASE app_db;
    \connect app_db
    GRANT ALL PRIVILEGES ON DATABASE app_db TO app_user;
    ALTER DATABASE app_db OWNER TO app_user;
EOSQL