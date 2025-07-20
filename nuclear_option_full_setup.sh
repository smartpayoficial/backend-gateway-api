#!/bin/bash

echo "💥 OPCIÓN NUCLEAR: SETUP COMPLETO DESDE CERO 💥"
echo "=============================================="

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${RED}⚠️  ESTA OPCIÓN VA A CREAR TODO DESDE CERO ⚠️${NC}"
echo "Esto incluye:"
echo "- Base de datos completamente nueva"
echo "- Estructura de tablas"
echo "- Datos de ejemplo realistas"
echo "- Configuración completa"
echo ""

read -p "¿Estás seguro? Esto eliminará cualquier dato existente (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Operación cancelada"
    exit 1
fi

echo ""
echo -e "${YELLOW}PASO 1: LIMPIEZA COMPLETA...${NC}"
docker-compose -f docker/Docker-compose.vps.yml down
docker volume rm postgres_data 2>/dev/null || echo "Volumen no existía"
docker volume create postgres_data

echo ""
echo -e "${YELLOW}PASO 2: INICIANDO SERVICIOS LIMPIOS...${NC}"
docker-compose -f docker/Docker-compose.vps.yml up -d
sleep 20

echo ""
echo -e "${YELLOW}PASO 3: CREANDO ESTRUCTURA COMPLETA VIA API...${NC}"
BASE_URL="http://localhost:8002"

# Esperar que la API esté lista
echo "Esperando que la API esté disponible..."
for i in {1..30}; do
    if curl -s "$BASE_URL/api/v1/countries/" >/dev/null 2>&1; then
        echo "API lista!"
        break
    fi
    echo -n "."
    sleep 2
done

echo ""
echo "Creando países completos..."
COUNTRIES=(
    '{"name": "Colombia", "code": "CO"}'
    '{"name": "México", "code": "MX"}'
    '{"name": "Argentina", "code": "AR"}'
    '{"name": "Chile", "code": "CL"}'
    '{"name": "Perú", "code": "PE"}'
    '{"name": "Brasil", "code": "BR"}'
    '{"name": "Ecuador", "code": "EC"}'
    '{"name": "Venezuela", "code": "VE"}'
    '{"name": "Uruguay", "code": "UY"}'
    '{"name": "Paraguay", "code": "PY"}'
)

for country in "${COUNTRIES[@]}"; do
    curl -s -X POST "$BASE_URL/api/v1/countries/" -H "Content-Type: application/json" -d "$country"
    echo ""
done

echo ""
echo "Obteniendo IDs de países..."
COLOMBIA_ID=$(curl -s "$BASE_URL/api/v1/countries/" | jq -r '.[] | select(.name=="Colombia") | .country_id')
MEXICO_ID=$(curl -s "$BASE_URL/api/v1/countries/" | jq -r '.[] | select(.name=="México") | .country_id')

echo "Colombia ID: $COLOMBIA_ID"
echo "México ID: $MEXICO_ID"

echo ""
echo "Creando regiones..."
if [ "$COLOMBIA_ID" != "null" ] && [ -n "$COLOMBIA_ID" ]; then
    REGIONS_CO=(
        "{\"name\": \"Bogotá D.C.\", \"country_id\": \"$COLOMBIA_ID\"}"
        "{\"name\": \"Antioquia\", \"country_id\": \"$COLOMBIA_ID\"}"
        "{\"name\": \"Valle del Cauca\", \"country_id\": \"$COLOMBIA_ID\"}"
        "{\"name\": \"Atlántico\", \"country_id\": \"$COLOMBIA_ID\"}"
        "{\"name\": \"Cundinamarca\", \"country_id\": \"$COLOMBIA_ID\"}"
    )
    
    for region in "${REGIONS_CO[@]}"; do
        curl -s -X POST "$BASE_URL/api/v1/regions/" -H "Content-Type: application/json" -d "$region"
        echo ""
    done
fi

if [ "$MEXICO_ID" != "null" ] && [ -n "$MEXICO_ID" ]; then
    REGIONS_MX=(
        "{\"name\": \"Ciudad de México\", \"country_id\": \"$MEXICO_ID\"}"
        "{\"name\": \"Jalisco\", \"country_id\": \"$MEXICO_ID\"}"
        "{\"name\": \"Nuevo León\", \"country_id\": \"$MEXICO_ID\"}"
    )
    
    for region in "${REGIONS_MX[@]}"; do
        curl -s -X POST "$BASE_URL/api/v1/regions/" -H "Content-Type: application/json" -d "$region"
        echo ""
    done
fi

echo ""
echo "Obteniendo IDs de regiones..."
BOGOTA_ID=$(curl -s "$BASE_URL/api/v1/regions/" | jq -r '.[] | select(.name=="Bogotá D.C.") | .region_id')
ANTIOQUIA_ID=$(curl -s "$BASE_URL/api/v1/regions/" | jq -r '.[] | select(.name=="Antioquia") | .region_id')

echo ""
echo "Creando ciudades..."
if [ "$BOGOTA_ID" != "null" ] && [ -n "$BOGOTA_ID" ]; then
    CITIES_BOGOTA=(
        "{\"name\": \"Bogotá\", \"region_id\": \"$BOGOTA_ID\"}"
        "{\"name\": \"Soacha\", \"region_id\": \"$BOGOTA_ID\"}"
        "{\"name\": \"Chía\", \"region_id\": \"$BOGOTA_ID\"}"
    )
    
    for city in "${CITIES_BOGOTA[@]}"; do
        curl -s -X POST "$BASE_URL/api/v1/cities/" -H "Content-Type: application/json" -d "$city"
        echo ""
    done
fi

if [ "$ANTIOQUIA_ID" != "null" ] && [ -n "$ANTIOQUIA_ID" ]; then
    CITIES_ANTIOQUIA=(
        "{\"name\": \"Medellín\", \"region_id\": \"$ANTIOQUIA_ID\"}"
        "{\"name\": \"Envigado\", \"region_id\": \"$ANTIOQUIA_ID\"}"
        "{\"name\": \"Itagüí\", \"region_id\": \"$ANTIOQUIA_ID\"}"
    )
    
    for city in "${CITIES_ANTIOQUIA[@]}"; do
        curl -s -X POST "$BASE_URL/api/v1/cities/" -H "Content-Type: application/json" -d "$city"
        echo ""
    done
fi

echo ""
echo "Creando planes de servicio..."
PLANS=(
    '{"name": "Básico", "description": "Plan básico para pequeños comercios - Hasta 5 dispositivos", "price": 29.99}'
    '{"name": "Profesional", "description": "Plan profesional para medianos comercios - Hasta 15 dispositivos", "price": 59.99}'
    '{"name": "Empresarial", "description": "Plan empresarial para grandes comercios - Hasta 50 dispositivos", "price": 99.99}'
    '{"name": "Premium", "description": "Plan premium ilimitado - Dispositivos ilimitados y soporte 24/7", "price": 149.99}'
)

for plan in "${PLANS[@]}"; do
    curl -s -X POST "$BASE_URL/api/v1/plans/" -H "Content-Type: application/json" -d "$plan"
    echo ""
done

echo ""
echo "Creando usuarios del sistema..."
USERS=(
    '{"email": "admin@smartpay.com", "name": "Administrador SmartPay", "password": "admin123"}'
    '{"email": "demo@tienda.com", "name": "Demo Store Owner", "password": "demo123"}'
    '{"email": "vendedor@tienda.com", "name": "Vendedor Demo", "password": "vendedor123"}'
    '{"email": "gerente@comercio.com", "name": "Gerente Comercio", "password": "gerente123"}'
)

for user in "${USERS[@]}"; do
    curl -s -X POST "$BASE_URL/api/v1/users/" -H "Content-Type: application/json" -d "$user"
    echo ""
done

echo ""
echo -e "${YELLOW}PASO 4: VERIFICACIÓN FINAL...${NC}"
echo ""
echo "📊 RESUMEN DE DATOS CREADOS:"
echo "Países: $(curl -s "$BASE_URL/api/v1/countries/" | jq '. | length')"
echo "Regiones: $(curl -s "$BASE_URL/api/v1/regions/" | jq '. | length')"
echo "Ciudades: $(curl -s "$BASE_URL/api/v1/cities/" | jq '. | length')"
echo "Planes: $(curl -s "$BASE_URL/api/v1/plans/" | jq '. | length')"
echo "Usuarios: $(curl -s "$BASE_URL/api/v1/users/" | jq '. | length')"
echo "Tiendas: $(curl -s "$BASE_URL/api/v1/stores/" | jq '. | length')"

echo ""
echo -e "${GREEN}💥 SETUP NUCLEAR COMPLETADO 💥${NC}"
echo ""
echo "🎉 ¡LA BASE DE DATOS ESTÁ COMPLETAMENTE FUNCIONAL!"
echo ""
echo "Credenciales de prueba:"
echo "- admin@smartpay.com / admin123"
echo "- demo@tienda.com / demo123"
echo ""
echo "Endpoints disponibles:"
echo "- http://localhost:8002/api/v1/countries/"
echo "- http://localhost:8002/api/v1/regions/"
echo "- http://localhost:8002/api/v1/cities/"
echo "- http://localhost:8002/api/v1/plans/"
echo "- http://localhost:8002/api/v1/users/"
echo "- http://localhost:8002/api/v1/stores/"
echo ""
echo "¡YA NO VAS A MORIR! 🚀"
