#!/bin/bash

echo "🔥 RECUPERACIÓN DE BASE DE DATOS DEV 🔥"
echo "======================================"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}1. BUSCANDO VOLUMEN smartpay_dev_db...${NC}"
if docker volume ls | grep -q "smartpay_dev_db"; then
    echo -e "${GREEN}✓ Volumen smartpay_dev_db encontrado!${NC}"
    docker volume inspect smartpay_dev_db
else
    echo -e "${RED}✗ Volumen smartpay_dev_db no encontrado${NC}"
    echo "Volúmenes disponibles:"
    docker volume ls
    echo ""
    echo "Buscando volúmenes similares..."
    docker volume ls | grep -i smartpay || echo "No se encontraron volúmenes smartpay"
    docker volume ls | grep -i dev || echo "No se encontraron volúmenes dev"
    exit 1
fi

echo ""
echo -e "${YELLOW}2. VERIFICANDO CONTENIDO DEL VOLUMEN DEV...${NC}"
echo "Explorando contenido de smartpay_dev_db:"
docker run --rm -v smartpay_dev_db:/data alpine sh -c "
echo 'Archivos en el volumen:';
ls -la /data/;
echo '';
echo 'Verificando si es una base de datos PostgreSQL:';
if [ -f /data/PG_VERSION ]; then
    echo 'Versión de PostgreSQL:';
    cat /data/PG_VERSION;
    echo '';
    echo 'Archivos de configuración:';
    ls -la /data/*.conf 2>/dev/null || echo 'No hay archivos de configuración';
    echo '';
    echo 'Bases de datos disponibles:';
    ls -la /data/base/ | head -10;
else
    echo 'No parece ser un volumen de PostgreSQL';
fi
"

echo ""
echo -e "${YELLOW}3. DETENIENDO SERVICIOS ACTUALES...${NC}"
docker-compose -f docker/Docker-compose.vps.yml down

echo ""
echo -e "${YELLOW}4. RESPALDANDO VOLUMEN ACTUAL...${NC}"
echo "Creando respaldo del volumen actual..."
docker volume create postgres_data_backup 2>/dev/null || echo "Backup ya existe"
docker run --rm \
    -v postgres_data:/source \
    -v postgres_data_backup:/backup \
    alpine sh -c "cp -a /source/. /backup/ 2>/dev/null || echo 'Volumen fuente vacío'"

echo ""
echo -e "${YELLOW}5. REEMPLAZANDO CON DATOS DEV...${NC}"
echo "Eliminando volumen actual..."
docker volume rm postgres_data 2>/dev/null || echo "Volumen no existía"

echo "Creando nuevo volumen..."
docker volume create postgres_data

echo "Copiando datos desde smartpay_dev_db..."
docker run --rm \
    -v smartpay_dev_db:/source \
    -v postgres_data:/dest \
    alpine sh -c "
    echo 'Copiando todos los archivos...';
    cp -a /source/. /dest/;
    echo 'Verificando copia:';
    ls -la /dest/ | head -10;
    echo 'Archivos copiados exitosamente';
"

echo ""
echo -e "${YELLOW}6. INICIANDO SERVICIOS CON DATOS RECUPERADOS...${NC}"
docker-compose -f docker/Docker-compose.vps.yml up -d

echo "Esperando que PostgreSQL esté listo..."
sleep 15

echo ""
echo -e "${YELLOW}7. VERIFICANDO RECUPERACIÓN...${NC}"
echo "Estado de contenedores:"
docker ps --filter "name=smartpay" --format "table {{.Names}}\t{{.Status}}"

echo ""
echo "Conectividad PostgreSQL:"
docker exec docker-smartpay-db-1 pg_isready -U postgres

echo ""
echo "Bases de datos disponibles:"
docker exec docker-smartpay-db-1 psql -U postgres -c "\l"

echo ""
echo "Verificando base de datos smartpay:"
DB_EXISTS=$(docker exec docker-smartpay-db-1 psql -U postgres -tAc "SELECT 1 FROM pg_database WHERE datname='smartpay'" 2>/dev/null)
if [ "$DB_EXISTS" = "1" ]; then
    echo -e "${GREEN}✓ Base de datos smartpay encontrada${NC}"
    
    echo ""
    echo "Tablas en smartpay:"
    docker exec docker-smartpay-db-1 psql -U postgres -d smartpay -c "\dt"
    
    echo ""
    echo "Conteo de registros por tabla:"
    docker exec docker-smartpay-db-1 psql -U postgres -d smartpay -c "
    SELECT 
        schemaname,
        tablename,
        n_live_tup as registros
    FROM pg_stat_user_tables 
    WHERE n_live_tup > 0
    ORDER BY n_live_tup DESC;" 2>/dev/null || echo "Error al obtener estadísticas"
    
else
    echo -e "${RED}✗ Base de datos smartpay no encontrada${NC}"
    echo "Intentando con smartpay_dev_db..."
    docker exec docker-smartpay-db-1 psql -U postgres -d smartpay_dev_db -c "\dt" 2>/dev/null || echo "smartpay_dev_db tampoco existe"
fi

echo ""
echo -e "${YELLOW}8. PROBANDO ENDPOINTS DESPUÉS DE RECUPERACIÓN...${NC}"
sleep 5
BASE_URL="http://localhost:8002"

echo "🔹 Países:"
curl -s -X GET "$BASE_URL/api/v1/countries/" | jq '. | length' 2>/dev/null || curl -s -X GET "$BASE_URL/api/v1/countries/"

echo "🔹 Usuarios:"
curl -s -X GET "$BASE_URL/api/v1/users/" | jq '. | length' 2>/dev/null || curl -s -X GET "$BASE_URL/api/v1/users/"

echo "🔹 Tiendas:"
curl -s -X GET "$BASE_URL/api/v1/stores/" | jq '. | length' 2>/dev/null || curl -s -X GET "$BASE_URL/api/v1/stores/"

echo ""
echo -e "${GREEN}🔥 RECUPERACIÓN COMPLETADA 🔥${NC}"
echo "Si los endpoints devuelven datos, ¡la recuperación fue exitosa!"
