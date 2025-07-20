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
echo "4. Si está vacío, ejecutamos el SQL de países y regiones:"
COUNTRY_COUNT=$(docker exec docker-smartpay-db-1 psql -U postgres -d smartpay -tAc "SELECT COUNT(*) FROM country;")

if [ "$COUNTRY_COUNT" -eq 0 ]; then
    echo "Ejecutando insert_countries_regions_cities.sql..."
    
    # Verificar si el archivo existe en el VPS
    if [ -f "/home/smartpayvps/db-smartpay/db/insert_countries_regions_cities.sql" ]; then
        echo "Archivo SQL encontrado, ejecutando..."
        docker exec -i docker-smartpay-db-1 psql -U postgres -d smartpay < /home/smartpayvps/db-smartpay/db/insert_countries_regions_cities.sql
        echo "✅ SQL ejecutado"
    elif [ -f "./db-smartpay/db/insert_countries_regions_cities.sql" ]; then
        echo "Archivo SQL local encontrado, ejecutando..."
        docker exec -i docker-smartpay-db-1 psql -U postgres -d smartpay < ./db-smartpay/db/insert_countries_regions_cities.sql
        echo "✅ SQL ejecutado"
    else
        echo "❌ Archivo SQL no encontrado, insertando países básicos..."
        curl -s -X POST "$BASE_URL/api/v1/countries/" -H "Content-Type: application/json" -d '{"name": "Colombia", "code": "CO"}'
        curl -s -X POST "$BASE_URL/api/v1/countries/" -H "Content-Type: application/json" -d '{"name": "México", "code": "MX"}'
        curl -s -X POST "$BASE_URL/api/v1/countries/" -H "Content-Type: application/json" -d '{"name": "Argentina", "code": "AR"}'
    fi
    
    echo ""
    echo "Verificando después de ejecutar SQL:"
    echo "Países insertados:"
    docker exec docker-smartpay-db-1 psql -U postgres -d smartpay -c "SELECT COUNT(*) as total_countries FROM country;"
    echo "Regiones insertadas:"
    docker exec docker-smartpay-db-1 psql -U postgres -d smartpay -c "SELECT COUNT(*) as total_regions FROM region;"
    echo "Ciudades insertadas:"
    docker exec docker-smartpay-db-1 psql -U postgres -d smartpay -c "SELECT COUNT(*) as total_cities FROM city;"
    
    echo ""
    echo "Endpoint /api/v1/countries/ después del SQL:"
    curl -s -X GET "$BASE_URL/api/v1/countries/"
else
    echo "Ya hay $COUNTRY_COUNT países en la base de datos"
fi

echo ""
echo "✅ Verificación completada"
