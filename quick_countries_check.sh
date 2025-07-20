#!/bin/bash

echo "🔍 VERIFICACIÓN RÁPIDA DE COUNTRIES 🔍"
echo "====================================="

BASE_URL="http://localhost:8002"

echo "1. Probando endpoint /api/v1/countries/:"
curl -s -X GET "$BASE_URL/api/v1/countries/"

echo ""
echo ""
echo "2. Verificando datos directamente en la base de datos:"
docker exec docker-smartpay-db-1 psql -U postgres -d smartpay -c "SELECT * FROM country LIMIT 10;"

echo ""
echo "3. Conteo total de países:"
docker exec docker-smartpay-db-1 psql -U postgres -d smartpay -c "SELECT COUNT(*) as total_countries FROM country;"

echo ""
echo "4. Si está vacío, agregamos algunos países básicos:"
COUNTRY_COUNT=$(docker exec docker-smartpay-db-1 psql -U postgres -d smartpay -tAc "SELECT COUNT(*) FROM country;")

if [ "$COUNTRY_COUNT" -eq 0 ]; then
    echo "Agregando países básicos..."
    curl -s -X POST "$BASE_URL/api/v1/countries/" -H "Content-Type: application/json" -d '{"name": "Colombia", "code": "CO"}'
    curl -s -X POST "$BASE_URL/api/v1/countries/" -H "Content-Type: application/json" -d '{"name": "México", "code": "MX"}'
    curl -s -X POST "$BASE_URL/api/v1/countries/" -H "Content-Type: application/json" -d '{"name": "Argentina", "code": "AR"}'
    
    echo ""
    echo "Verificando después de agregar:"
    curl -s -X GET "$BASE_URL/api/v1/countries/"
else
    echo "Ya hay $COUNTRY_COUNT países en la base de datos"
fi

echo ""
echo "✅ Verificación completada"
