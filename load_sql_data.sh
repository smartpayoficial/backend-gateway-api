#!/bin/bash

echo "🔥 CARGANDO DATOS DESDE ARCHIVOS SQL 🔥"
echo "======================================"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}1. VERIFICANDO ARCHIVOS SQL DISPONIBLES...${NC}"
if [ -d "/home/smartpayvps/db-smartpay/db" ]; then
    echo "Archivos SQL encontrados:"
    ls -la /home/smartpayvps/db-smartpay/db/
    echo ""
    
    echo -e "${YELLOW}2. EJECUTANDO ARCHIVOS SQL...${NC}"
    
    # Ejecutar create.sql si existe
    if [ -f "/home/smartpayvps/db-smartpay/db/create.sql" ]; then
        echo "Ejecutando create.sql..."
        docker exec -i docker-smartpay-db-1 psql -U postgres -d smartpay < /home/smartpayvps/db-smartpay/db/create.sql
        echo ""
    fi
    
    # Ejecutar insert_countries_regions_cities.sql si existe
    if [ -f "/home/smartpayvps/db-smartpay/db/insert_countries_regions_cities.sql" ]; then
        echo "Ejecutando insert_countries_regions_cities.sql..."
        docker exec -i docker-smartpay-db-1 psql -U postgres -d smartpay < /home/smartpayvps/db-smartpay/db/insert_countries_regions_cities.sql
        echo ""
    fi
    
    # Ejecutar add_store_table.sql si existe
    if [ -f "/home/smartpayvps/db-smartpay/db/add_store_table.sql" ]; then
        echo "Ejecutando add_store_table.sql..."
        docker exec -i docker-smartpay-db-1 psql -U postgres -d smartpay < /home/smartpayvps/db-smartpay/db/add_store_table.sql
        echo ""
    fi
    
    # Ejecutar cualquier otro archivo SQL
    for sql_file in /home/smartpayvps/db-smartpay/db/*.sql; do
        if [ -f "$sql_file" ]; then
            filename=$(basename "$sql_file")
            if [[ "$filename" != "create.sql" && "$filename" != "insert_countries_regions_cities.sql" && "$filename" != "add_store_table.sql" ]]; then
                echo "Ejecutando $filename..."
                docker exec -i docker-smartpay-db-1 psql -U postgres -d smartpay < "$sql_file"
                echo ""
            fi
        fi
    done
    
else
    echo "Directorio /home/smartpayvps/db-smartpay/db no encontrado"
    echo "Copiando archivos desde el directorio local..."
    
    if [ -d "./db-smartpay" ]; then
        echo "Ejecutando archivos SQL locales..."
        for sql_file in ./db-smartpay/db/*.sql; do
            if [ -f "$sql_file" ]; then
                echo "Ejecutando $(basename "$sql_file")..."
                docker exec -i docker-smartpay-db-1 psql -U postgres -d smartpay < "$sql_file"
                echo ""
            fi
        done
    else
        echo "No se encontraron archivos SQL"
    fi
fi

echo ""
echo -e "${YELLOW}3. VERIFICANDO DATOS CARGADOS...${NC}"

echo "Conteo de registros por tabla:"
docker exec docker-smartpay-db-1 psql -U postgres -d smartpay -c "
SELECT 
    schemaname,
    tablename,
    n_live_tup as registros
FROM pg_stat_user_tables 
WHERE n_live_tup > 0
ORDER BY n_live_tup DESC;
"

echo ""
echo "Verificando tablas principales:"
echo "📊 Países:"
docker exec docker-smartpay-db-1 psql -U postgres -d smartpay -c "SELECT COUNT(*) FROM country;"

echo "📊 Regiones:"
docker exec docker-smartpay-db-1 psql -U postgres -d smartpay -c "SELECT COUNT(*) FROM region;"

echo "📊 Ciudades:"
docker exec docker-smartpay-db-1 psql -U postgres -d smartpay -c "SELECT COUNT(*) FROM city;"

echo "📊 Tiendas:"
docker exec docker-smartpay-db-1 psql -U postgres -d smartpay -c "SELECT COUNT(*) FROM store;"

echo "📊 Usuarios:"
docker exec docker-smartpay-db-1 psql -U postgres -d smartpay -c "SELECT COUNT(*) FROM \"user\";"

echo "📊 Dispositivos:"
docker exec docker-smartpay-db-1 psql -U postgres -d smartpay -c "SELECT COUNT(*) FROM device;"

echo "📊 Pagos:"
docker exec docker-smartpay-db-1 psql -U postgres -d smartpay -c "SELECT COUNT(*) FROM payment;"

echo ""
echo -e "${YELLOW}4. PROBANDO ENDPOINTS DESPUÉS DE CARGAR DATOS...${NC}"
BASE_URL="http://localhost:8002"

echo "🔹 GET /api/v1/countries/"
curl -s -X GET "$BASE_URL/api/v1/countries/" | jq '. | length' 2>/dev/null || curl -s -X GET "$BASE_URL/api/v1/countries/"

echo ""
echo "🔹 GET /api/v1/regions/"
curl -s -X GET "$BASE_URL/api/v1/regions/" | jq '. | length' 2>/dev/null || curl -s -X GET "$BASE_URL/api/v1/regions/"

echo ""
echo "🔹 GET /api/v1/cities/"
curl -s -X GET "$BASE_URL/api/v1/cities/" | jq '. | length' 2>/dev/null || curl -s -X GET "$BASE_URL/api/v1/cities/"

echo ""
echo "🔹 GET /api/v1/stores/"
curl -s -X GET "$BASE_URL/api/v1/stores/" | jq '. | length' 2>/dev/null || curl -s -X GET "$BASE_URL/api/v1/stores/"

echo ""
echo "🔹 GET /api/v1/users/"
curl -s -X GET "$BASE_URL/api/v1/users/" | jq '. | length' 2>/dev/null || curl -s -X GET "$BASE_URL/api/v1/users/"

echo ""
echo -e "${GREEN}🔥 CARGA DE DATOS SQL COMPLETADA 🔥${NC}"
echo ""
echo "¡Si los endpoints devuelven números > 0, los datos se cargaron exitosamente!"
