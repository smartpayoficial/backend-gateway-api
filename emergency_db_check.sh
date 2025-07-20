#!/bin/bash

echo "🚨 DIAGNÓSTICO DE EMERGENCIA - BASE DE DATOS 🚨"
echo "================================================"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}1. VERIFICANDO CONTENEDORES...${NC}"
docker ps --filter "name=smartpay" --format "table {{.Names}}\t{{.Status}}"
echo ""

echo -e "${YELLOW}2. VERIFICANDO VOLÚMENES Y SUS CONTENIDOS...${NC}"
echo "Volúmenes disponibles:"
docker volume ls | grep -E "(postgres|smartpay)"
echo ""

echo "Contenido del volumen postgres_data:"
docker run --rm -v postgres_data:/data alpine ls -la /data
echo ""

echo "Contenido del volumen docker_postgres_data:"
docker run --rm -v docker_postgres_data:/data alpine ls -la /data 2>/dev/null || echo "Volumen no accesible"
echo ""

echo -e "${YELLOW}3. VERIFICANDO BASE DE DATOS POSTGRESQL...${NC}"
echo "Conectividad:"
docker exec docker-smartpay-db-1 pg_isready -U postgres

echo ""
echo "Bases de datos existentes:"
docker exec docker-smartpay-db-1 psql -U postgres -c "\l"

echo ""
echo "Verificando si existe la base de datos 'smartpay':"
DB_EXISTS=$(docker exec docker-smartpay-db-1 psql -U postgres -tAc "SELECT 1 FROM pg_database WHERE datname='smartpay'")
if [ "$DB_EXISTS" = "1" ]; then
    echo -e "${GREEN}✓ Base de datos 'smartpay' existe${NC}"
    
    echo ""
    echo "Tablas en la base de datos smartpay:"
    docker exec docker-smartpay-db-1 psql -U postgres -d smartpay -c "\dt"
    
    echo ""
    echo "Conteo de registros en tablas principales:"
    docker exec docker-smartpay-db-1 psql -U postgres -d smartpay -c "
    SELECT 
        schemaname,
        tablename,
        n_tup_ins as inserts,
        n_tup_upd as updates,
        n_tup_del as deletes,
        n_live_tup as live_rows,
        n_dead_tup as dead_rows
    FROM pg_stat_user_tables 
    ORDER BY n_live_tup DESC;" 2>/dev/null || echo "No se pueden obtener estadísticas"
    
else
    echo -e "${RED}✗ Base de datos 'smartpay' NO EXISTE${NC}"
fi

echo ""
echo -e "${YELLOW}4. VERIFICANDO LOGS DE LA APLICACIÓN...${NC}"
echo "Logs recientes del backend-api:"
docker logs backend-api --tail 10

echo ""
echo "Logs recientes del smartpay-db-api:"
docker logs smartpay-db-api --tail 10

echo ""
echo -e "${YELLOW}5. VERIFICANDO ARCHIVOS DE MIGRACIÓN...${NC}"
if [ -d "app/db" ]; then
    echo "Archivos de migración encontrados:"
    find app/db -name "*.py" -o -name "*.sql" | head -10
else
    echo "No se encontró directorio app/db"
fi

if [ -d "alembic" ]; then
    echo "Directorio alembic encontrado:"
    ls -la alembic/
else
    echo "No se encontró directorio alembic"
fi

echo ""
echo "🚨 DIAGNÓSTICO COMPLETADO 🚨"
