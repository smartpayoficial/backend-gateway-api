#!/bin/bash

echo "🔍 PRUEBA COMPLETA DE ENDPOINTS API 🔍"
echo "===================================="

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

BASE_URL="http://localhost:8002"
GATEWAY_URL="http://localhost:8000"

echo -e "${YELLOW}1. VERIFICANDO ESTADO DE SERVICIOS:${NC}"
docker ps --filter "name=smartpay" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo -e "${YELLOW}2. PROBANDO ENDPOINTS DE DB-API (Puerto 8002):${NC}"

echo "🔹 GET /api/v1/countries/"
curl -s -X GET "$BASE_URL/api/v1/countries/" | jq . 2>/dev/null || curl -s -X GET "$BASE_URL/api/v1/countries/"
echo ""

echo "🔹 GET /api/v1/cities/"
curl -s -X GET "$BASE_URL/api/v1/cities/" | jq . 2>/dev/null || curl -s -X GET "$BASE_URL/api/v1/cities/"
echo ""

echo "🔹 GET /api/v1/regions/"
curl -s -X GET "$BASE_URL/api/v1/regions/" | jq . 2>/dev/null || curl -s -X GET "$BASE_URL/api/v1/regions/"
echo ""

echo "🔹 GET /api/v1/plans/"
curl -s -X GET "$BASE_URL/api/v1/plans/" | jq . 2>/dev/null || curl -s -X GET "$BASE_URL/api/v1/plans/"
echo ""

echo "🔹 GET /api/v1/stores/"
curl -s -X GET "$BASE_URL/api/v1/stores/" | jq . 2>/dev/null || curl -s -X GET "$BASE_URL/api/v1/stores/"
echo ""

echo "🔹 GET /api/v1/users/"
curl -s -X GET "$BASE_URL/api/v1/users/" | jq . 2>/dev/null || curl -s -X GET "$BASE_URL/api/v1/users/"
echo ""

echo -e "${YELLOW}3. PROBANDO ENDPOINTS DE GATEWAY (Puerto 8000):${NC}"

echo "🔹 GET /api/v1/stores (Gateway)"
curl -s -X GET "$GATEWAY_URL/api/v1/stores" | jq . 2>/dev/null || curl -s -X GET "$GATEWAY_URL/api/v1/stores"
echo ""

echo "🔹 GET /api/v1/countries (Gateway)"
curl -s -X GET "$GATEWAY_URL/api/v1/countries" | jq . 2>/dev/null || curl -s -X GET "$GATEWAY_URL/api/v1/countries"
echo ""

echo -e "${YELLOW}4. VERIFICANDO LOGS DE ERRORES:${NC}"
echo "Logs del smartpay-db-api:"
docker logs smartpay-db-api --tail 15
echo ""

echo "Logs del backend-api (gateway):"
docker logs backend-api --tail 15
echo ""

echo -e "${YELLOW}5. PROBANDO CONECTIVIDAD DIRECTA A LA BASE DE DATOS:${NC}"
echo "Verificando datos directamente en la BD:"
docker exec docker-smartpay-db-1 psql -U postgres -d smartpay -c "
SELECT 'countries' as tabla, COUNT(*) as total FROM country
UNION ALL
SELECT 'stores' as tabla, COUNT(*) as total FROM store
UNION ALL  
SELECT 'users' as tabla, COUNT(*) as total FROM \"user\"
UNION ALL
SELECT 'cities' as tabla, COUNT(*) as total FROM city
UNION ALL
SELECT 'plans' as tabla, COUNT(*) as total FROM plan;
"

echo ""
echo -e "${YELLOW}6. VERIFICANDO CONFIGURACIÓN DE BASE DE DATOS:${NC}"
echo "Variables de entorno del smartpay-db-api:"
docker exec smartpay-db-api env | grep -E "(POSTGRES|DATABASE)" || echo "No se encontraron variables de BD"

echo ""
echo "Variables de entorno del backend-api:"
docker exec backend-api env | grep -E "(DB_API|USER_SVC)" || echo "No se encontraron variables de conexión"

echo ""
echo -e "${YELLOW}7. PROBANDO ENDPOINTS ESPECÍFICOS:${NC}"

# Probar endpoints específicos que sabemos que deberían funcionar
echo "🔹 Health check DB-API:"
curl -s -X GET "$BASE_URL/health" 2>/dev/null || curl -s -X GET "$BASE_URL/" || echo "No responde"

echo ""
echo "🔹 Health check Gateway:"
curl -s -X GET "$GATEWAY_URL/health" 2>/dev/null || curl -s -X GET "$GATEWAY_URL/" || echo "No responde"

echo ""
echo "🔹 Docs DB-API:"
curl -s -X GET "$BASE_URL/docs" | head -5 2>/dev/null || echo "Docs no disponibles"

echo ""
echo -e "${GREEN}🔍 PRUEBA DE ENDPOINTS COMPLETADA 🔍${NC}"
