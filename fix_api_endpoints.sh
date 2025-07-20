#!/bin/bash

echo "🚑 REPARACIÓN DE ENDPOINTS API 🚑"
echo "================================="

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}PASO 1: Verificar y poblar datos si están vacíos${NC}"
./populate_data_emergency.sh

echo ""
echo -e "${YELLOW}PASO 2: Reiniciar servicios completamente${NC}"
echo "Deteniendo todos los servicios..."
docker-compose -f docker/Docker-compose.vps.yml down

echo "Eliminando contenedores para forzar recreación..."
docker rm -f backend-api smartpay-db-api docker-smartpay-db-1 2>/dev/null || echo "Contenedores ya eliminados"

echo "Iniciando servicios desde cero..."
docker-compose -f docker/Docker-compose.vps.yml up -d

echo "Esperando que los servicios estén listos..."
sleep 20

echo ""
echo -e "${YELLOW}PASO 3: Verificar conectividad de base de datos${NC}"
echo "Esperando PostgreSQL..."
for i in {1..30}; do
    if docker exec docker-smartpay-db-1 pg_isready -U postgres >/dev/null 2>&1; then
        echo -e "${GREEN}✓ PostgreSQL listo${NC}"
        break
    fi
    echo -n "."
    sleep 2
done

echo ""
echo -e "${YELLOW}PASO 4: Verificar que la DB-API puede conectarse${NC}"
echo "Logs recientes de smartpay-db-api:"
docker logs smartpay-db-api --tail 10

echo ""
echo -e "${YELLOW}PASO 5: Probar endpoints básicos${NC}"
BASE_URL="http://localhost:8002"

echo "🔹 Probando /api/v1/countries/"
COUNTRIES_RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/countries/")
echo "Respuesta: $COUNTRIES_RESPONSE"

if [[ "$COUNTRIES_RESPONSE" == "[]" ]] || [[ -z "$COUNTRIES_RESPONSE" ]]; then
    echo -e "${RED}⚠️ Endpoint vacío, insertando datos directamente...${NC}"
    
    # Insertar datos directamente si los endpoints están vacíos
    docker exec docker-smartpay-db-1 psql -U postgres -d smartpay -c "
    -- Limpiar y reinsertar países
    TRUNCATE country CASCADE;
    INSERT INTO country (id, name, code, created_at) VALUES 
    (1, 'Colombia', 'CO', NOW()),
    (2, 'México', 'MX', NOW()),
    (3, 'Argentina', 'AR', NOW()),
    (4, 'Chile', 'CL', NOW()),
    (5, 'Perú', 'PE', NOW());
    
    -- Reiniciar secuencia
    SELECT setval('country_id_seq', 5);
    "
    
    echo "Datos insertados, probando endpoint nuevamente..."
    sleep 5
    curl -s -X GET "$BASE_URL/api/v1/countries/"
fi

echo ""
echo -e "${YELLOW}PASO 6: Verificar estructura de tablas${NC}"
echo "Verificando que las tablas tengan las columnas correctas:"
docker exec docker-smartpay-db-1 psql -U postgres -d smartpay -c "\d country"

echo ""
echo -e "${YELLOW}PASO 7: Probar crear un país via API${NC}"
echo "Intentando crear un país via POST:"
curl -s -X POST "$BASE_URL/api/v1/countries/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Country", "code": "TC"}'

echo ""
echo ""
echo -e "${YELLOW}PASO 8: Verificación final de todos los endpoints${NC}"
./test_api_endpoints.sh

echo ""
echo -e "${GREEN}🚑 REPARACIÓN DE ENDPOINTS COMPLETADA 🚑${NC}"
