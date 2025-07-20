#!/bin/bash

echo "🚀 POBLANDO DATOS CON ESTRUCTURA CORRECTA 🚀"
echo "============================================"

BASE_URL="http://localhost:8002"

echo "1. Creando países..."
curl -s -X POST "$BASE_URL/api/v1/countries/" -H "Content-Type: application/json" -d '{"name": "Colombia", "code": "CO"}'
curl -s -X POST "$BASE_URL/api/v1/countries/" -H "Content-Type: application/json" -d '{"name": "México", "code": "MX"}'
curl -s -X POST "$BASE_URL/api/v1/countries/" -H "Content-Type: application/json" -d '{"name": "Argentina", "code": "AR"}'
curl -s -X POST "$BASE_URL/api/v1/countries/" -H "Content-Type: application/json" -d '{"name": "Chile", "code": "CL"}'
curl -s -X POST "$BASE_URL/api/v1/countries/" -H "Content-Type: application/json" -d '{"name": "Perú", "code": "PE"}'

echo ""
echo "2. Verificando países creados:"
curl -s -X GET "$BASE_URL/api/v1/countries/" | jq .

echo ""
echo "3. Obteniendo ID de Colombia para crear regiones..."
COLOMBIA_ID=$(curl -s -X GET "$BASE_URL/api/v1/countries/" | jq -r '.[] | select(.name=="Colombia") | .country_id')
echo "Colombia ID: $COLOMBIA_ID"

if [ "$COLOMBIA_ID" != "null" ] && [ -n "$COLOMBIA_ID" ]; then
    echo "4. Creando regiones para Colombia..."
    curl -s -X POST "$BASE_URL/api/v1/regions/" -H "Content-Type: application/json" -d "{\"name\": \"Bogotá D.C.\", \"country_id\": \"$COLOMBIA_ID\"}"
    curl -s -X POST "$BASE_URL/api/v1/regions/" -H "Content-Type: application/json" -d "{\"name\": \"Antioquia\", \"country_id\": \"$COLOMBIA_ID\"}"
    curl -s -X POST "$BASE_URL/api/v1/regions/" -H "Content-Type: application/json" -d "{\"name\": \"Valle del Cauca\", \"country_id\": \"$COLOMBIA_ID\"}"
    
    echo ""
    echo "5. Verificando regiones:"
    curl -s -X GET "$BASE_URL/api/v1/regions/" | jq .
    
    echo ""
    echo "6. Obteniendo ID de Bogotá para crear ciudades..."
    BOGOTA_ID=$(curl -s -X GET "$BASE_URL/api/v1/regions/" | jq -r '.[] | select(.name=="Bogotá D.C.") | .region_id')
    echo "Bogotá ID: $BOGOTA_ID"
    
    if [ "$BOGOTA_ID" != "null" ] && [ -n "$BOGOTA_ID" ]; then
        echo "7. Creando ciudades para Bogotá..."
        curl -s -X POST "$BASE_URL/api/v1/cities/" -H "Content-Type: application/json" -d "{\"name\": \"Bogotá\", \"region_id\": \"$BOGOTA_ID\"}"
        curl -s -X POST "$BASE_URL/api/v1/cities/" -H "Content-Type: application/json" -d "{\"name\": \"Soacha\", \"region_id\": \"$BOGOTA_ID\"}"
        
        echo ""
        echo "8. Verificando ciudades:"
        curl -s -X GET "$BASE_URL/api/v1/cities/" | jq .
    fi
fi

echo ""
echo "9. Creando planes..."
curl -s -X POST "$BASE_URL/api/v1/plans/" -H "Content-Type: application/json" -d '{"name": "Básico", "description": "Plan básico", "price": 29.99}'
curl -s -X POST "$BASE_URL/api/v1/plans/" -H "Content-Type: application/json" -d '{"name": "Profesional", "description": "Plan profesional", "price": 59.99}'
curl -s -X POST "$BASE_URL/api/v1/plans/" -H "Content-Type: application/json" -d '{"name": "Empresarial", "description": "Plan empresarial", "price": 99.99}'

echo ""
echo "10. Verificando planes:"
curl -s -X GET "$BASE_URL/api/v1/plans/" | jq .

echo ""
echo "11. Creando usuarios..."
curl -s -X POST "$BASE_URL/api/v1/users/" -H "Content-Type: application/json" -d '{"email": "admin@smartpay.com", "name": "Administrador", "password": "admin123"}'
curl -s -X POST "$BASE_URL/api/v1/users/" -H "Content-Type: application/json" -d '{"email": "demo@tienda.com", "name": "Demo User", "password": "demo123"}'

echo ""
echo "12. Verificando usuarios:"
curl -s -X GET "$BASE_URL/api/v1/users/" | jq .

echo ""
echo "13. VERIFICACIÓN FINAL - Todos los endpoints:"
echo "📊 Países:"
curl -s -X GET "$BASE_URL/api/v1/countries/" | jq '. | length'

echo "📊 Regiones:"
curl -s -X GET "$BASE_URL/api/v1/regions/" | jq '. | length'

echo "📊 Ciudades:"
curl -s -X GET "$BASE_URL/api/v1/cities/" | jq '. | length'

echo "📊 Planes:"
curl -s -X GET "$BASE_URL/api/v1/plans/" | jq '. | length'

echo "📊 Usuarios:"
curl -s -X GET "$BASE_URL/api/v1/users/" | jq '. | length'

echo "📊 Tiendas:"
curl -s -X GET "$BASE_URL/api/v1/stores/" | jq '. | length'

echo ""
echo "🎉 ¡DATOS POBLADOS EXITOSAMENTE! 🎉"
echo "¡Los endpoints ya NO están vacíos!"
