#!/bin/bash

echo "🔥 VERIFICACIÓN URGENTE DE DATOS 🔥"
echo "=================================="

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${YELLOW}1. CONTANDO REGISTROS EN TODAS LAS TABLAS:${NC}"
docker exec docker-smartpay-db-1 psql -U postgres -d smartpay -c "
DO \$\$
DECLARE
    table_name TEXT;
    row_count INTEGER;
BEGIN
    FOR table_name IN 
        SELECT tablename FROM pg_tables WHERE schemaname = 'public'
    LOOP
        EXECUTE 'SELECT COUNT(*) FROM ' || table_name INTO row_count;
        RAISE NOTICE '% tiene % registros', table_name, row_count;
    END LOOP;
END
\$\$;
"

echo ""
echo -e "${YELLOW}2. VERIFICANDO TABLAS ESPECÍFICAS:${NC}"
echo "Tabla STORE:"
docker exec docker-smartpay-db-1 psql -U postgres -d smartpay -c "SELECT COUNT(*) as total_stores FROM store;"
docker exec docker-smartpay-db-1 psql -U postgres -d smartpay -c "SELECT * FROM store LIMIT 5;"

echo ""
echo "Tabla USER:"
docker exec docker-smartpay-db-1 psql -U postgres -d smartpay -c "SELECT COUNT(*) as total_users FROM \"user\";"
docker exec docker-smartpay-db-1 psql -U postgres -d smartpay -c "SELECT * FROM \"user\" LIMIT 5;"

echo ""
echo "Tabla COUNTRY:"
docker exec docker-smartpay-db-1 psql -U postgres -d smartpay -c "SELECT COUNT(*) as total_countries FROM country;"
docker exec docker-smartpay-db-1 psql -U postgres -d smartpay -c "SELECT * FROM country LIMIT 5;"

echo ""
echo "Tabla DEVICE:"
docker exec docker-smartpay-db-1 psql -U postgres -d smartpay -c "SELECT COUNT(*) as total_devices FROM device;"

echo ""
echo "Tabla PAYMENT:"
docker exec docker-smartpay-db-1 psql -U postgres -d smartpay -c "SELECT COUNT(*) as total_payments FROM payment;"

echo ""
echo -e "${YELLOW}3. VERIFICANDO SI HAY DATOS EN EL VOLUMEN ANTERIOR:${NC}"
echo "Verificando docker_postgres_data (volumen anterior):"
docker run --rm -v docker_postgres_data:/old_data alpine sh -c "
echo 'Archivos de base de datos en volumen anterior:';
ls -la /old_data/base/;
echo '';
echo 'Verificando si hay archivos de datos específicos:';
find /old_data -name '*.dat' -o -name 'base' | head -10;
"

echo ""
echo -e "${YELLOW}4. PROBANDO RESTAURAR DESDE VOLUMEN ANTERIOR:${NC}"
echo "Deteniendo servicios para migración completa..."
docker-compose -f docker/Docker-compose.vps.yml down

echo "Eliminando volumen actual y recreando desde el anterior..."
docker volume rm postgres_data 2>/dev/null || echo "Volumen no existía"
docker volume create postgres_data

echo "Copiando TODOS los datos del volumen anterior..."
docker run --rm \
    -v docker_postgres_data:/source \
    -v postgres_data:/dest \
    alpine sh -c "
    echo 'Copiando archivos...';
    cp -a /source/. /dest/;
    echo 'Verificando copia:';
    ls -la /dest/ | head -10;
    echo 'Archivos copiados exitosamente';
"

echo "Reiniciando servicios..."
docker-compose -f docker/Docker-compose.vps.yml up -d

echo "Esperando que PostgreSQL esté listo..."
sleep 15

echo ""
echo -e "${GREEN}5. VERIFICACIÓN FINAL DESPUÉS DE RESTAURACIÓN:${NC}"
echo "Conectividad:"
docker exec docker-smartpay-db-1 pg_isready -U postgres

echo ""
echo "Bases de datos:"
docker exec docker-smartpay-db-1 psql -U postgres -c "\l"

echo ""
echo "Conteo final de registros:"
docker exec docker-smartpay-db-1 psql -U postgres -d smartpay -c "
SELECT 
    'store' as tabla, COUNT(*) as registros FROM store
UNION ALL
SELECT 
    'user' as tabla, COUNT(*) as registros FROM \"user\"
UNION ALL
SELECT 
    'country' as tabla, COUNT(*) as registros FROM country
UNION ALL
SELECT 
    'device' as tabla, COUNT(*) as registros FROM device
UNION ALL
SELECT 
    'payment' as tabla, COUNT(*) as registros FROM payment;
"

echo ""
echo -e "${GREEN}🔥 VERIFICACIÓN COMPLETADA 🔥${NC}"
