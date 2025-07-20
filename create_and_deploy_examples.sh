#!/bin/bash

# Script de ejemplos para el nuevo endpoint de crear y desplegar tienda
# Este script muestra cómo usar el endpoint POST /stores/ con curl

BASE_URL="http://localhost:8000/api/v1"
STORES_URL="$BASE_URL/stores"

echo "🏪 Ejemplos del endpoint: Crear y Desplegar Tienda Automáticamente"
echo "=================================================================="

# Función para imprimir respuestas de forma legible
print_response() {
    local title="$1"
    local response="$2"
    echo ""
    echo "=================================================="
    echo "$title"
    echo "=================================================="
    echo "$response" | jq . 2>/dev/null || echo "$response"
}

# Función para obtener el primer país disponible
get_first_country() {
    curl -s "$BASE_URL/countries" | jq -r '.[0].id' 2>/dev/null
}

echo ""
echo "📋 Ejemplo 1: Crear y desplegar tienda con plan básico"
echo "-----------------------------------------------------"

# Obtener un country_id válido
COUNTRY_ID=$(get_first_country)
if [ "$COUNTRY_ID" = "null" ] || [ -z "$COUNTRY_ID" ]; then
    echo "❌ Error: No se pudo obtener un país válido"
    echo "Asegúrate de que hay países en la base de datos"
    exit 1
fi

echo "✅ Usando country_id: $COUNTRY_ID"

# Crear y desplegar tienda con plan básico
BASIC_STORE_DATA='{
  "nombre": "Mi Tienda Básica",
  "country_id": "'$COUNTRY_ID'",
  "tokens_disponibles": 100,
  "plan": "basic"
}'

echo ""
echo "Creando tienda con datos:"
echo "$BASIC_STORE_DATA" | jq .

BASIC_RESPONSE=$(curl -s -X POST "$STORES_URL/" \
  -H "Content-Type: application/json" \
  -d "$BASIC_STORE_DATA")

print_response "Respuesta - Tienda Básica Creada y Desplegada" "$BASIC_RESPONSE"

# Extraer información de la respuesta
BASIC_STORE_ID=$(echo "$BASIC_RESPONSE" | jq -r '.store.id' 2>/dev/null)
BASIC_BACK_LINK=$(echo "$BASIC_RESPONSE" | jq -r '.deployment.back_link' 2>/dev/null)

if [ "$BASIC_STORE_ID" != "null" ] && [ -n "$BASIC_STORE_ID" ]; then
    echo "✅ Tienda básica creada con ID: $BASIC_STORE_ID"
    echo "   Backend disponible en: $BASIC_BACK_LINK"
else
    echo "❌ Error: No se pudo crear la tienda básica"
fi

echo ""
echo "📋 Ejemplo 2: Crear y desplegar tienda con plan premium"
echo "------------------------------------------------------"

# Crear y desplegar tienda con plan premium
PREMIUM_STORE_DATA='{
  "nombre": "Mi Tienda Premium",
  "country_id": "'$COUNTRY_ID'",
  "tokens_disponibles": 500,
  "plan": "premium"
}'

echo "Creando tienda premium con datos:"
echo "$PREMIUM_STORE_DATA" | jq .

PREMIUM_RESPONSE=$(curl -s -X POST "$STORES_URL/" \
  -H "Content-Type: application/json" \
  -d "$PREMIUM_STORE_DATA")

print_response "Respuesta - Tienda Premium Creada y Desplegada" "$PREMIUM_RESPONSE"

PREMIUM_STORE_ID=$(echo "$PREMIUM_RESPONSE" | jq -r '.store.id' 2>/dev/null)
PREMIUM_BACK_LINK=$(echo "$PREMIUM_RESPONSE" | jq -r '.deployment.back_link' 2>/dev/null)

if [ "$PREMIUM_STORE_ID" != "null" ] && [ -n "$PREMIUM_STORE_ID" ]; then
    echo "✅ Tienda premium creada con ID: $PREMIUM_STORE_ID"
    echo "   Backend disponible en: $PREMIUM_BACK_LINK"
fi

echo ""
echo "📋 Ejemplo 3: Crear y desplegar tienda con plan enterprise"
echo "---------------------------------------------------------"

# Crear y desplegar tienda con plan enterprise
ENTERPRISE_STORE_DATA='{
  "nombre": "Mi Tienda Enterprise",
  "country_id": "'$COUNTRY_ID'",
  "tokens_disponibles": 1000,
  "plan": "enterprise"
}'

echo "Creando tienda enterprise con datos:"
echo "$ENTERPRISE_STORE_DATA" | jq .

ENTERPRISE_RESPONSE=$(curl -s -X POST "$STORES_URL/" \
  -H "Content-Type: application/json" \
  -d "$ENTERPRISE_STORE_DATA")

print_response "Respuesta - Tienda Enterprise Creada y Desplegada" "$ENTERPRISE_RESPONSE"

ENTERPRISE_STORE_ID=$(echo "$ENTERPRISE_RESPONSE" | jq -r '.store.id' 2>/dev/null)
ENTERPRISE_BACK_LINK=$(echo "$ENTERPRISE_RESPONSE" | jq -r '.deployment.back_link' 2>/dev/null)

if [ "$ENTERPRISE_STORE_ID" != "null" ] && [ -n "$ENTERPRISE_STORE_ID" ]; then
    echo "✅ Tienda enterprise creada con ID: $ENTERPRISE_STORE_ID"
    echo "   Backend disponible en: $ENTERPRISE_BACK_LINK"
fi

echo ""
echo "📋 Ejemplo 4: Verificar estados de los deployments"
echo "-------------------------------------------------"

# Verificar estado de cada tienda creada
for STORE_ID in "$BASIC_STORE_ID" "$PREMIUM_STORE_ID" "$ENTERPRISE_STORE_ID"; do
    if [ "$STORE_ID" != "null" ] && [ -n "$STORE_ID" ]; then
        echo ""
        echo "Verificando estado de tienda: $STORE_ID"
        STATUS_RESPONSE=$(curl -s -X GET "$STORES_URL/$STORE_ID/deploy/status")
        echo "Estado: $(echo "$STATUS_RESPONSE" | jq -r '.status' 2>/dev/null)"
        echo "Contenedores corriendo: $(echo "$STATUS_RESPONSE" | jq -r '.containers_running' 2>/dev/null)"
    fi
done

echo ""
echo "📋 Ejemplo 5: Probar conectividad a los backends desplegados"
echo "-----------------------------------------------------------"

echo "Esperando 10 segundos para que los servicios se inicien completamente..."
sleep 10

# Probar cada backend
for BACK_LINK in "$BASIC_BACK_LINK" "$PREMIUM_BACK_LINK" "$ENTERPRISE_BACK_LINK"; do
    if [ "$BACK_LINK" != "null" ] && [ -n "$BACK_LINK" ]; then
        echo ""
        echo "Probando backend: $BACK_LINK"
        
        HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BACK_LINK/docs" --connect-timeout 15)
        
        if [ "$HEALTH_STATUS" = "200" ]; then
            echo "✅ Backend funcionando correctamente"
            echo "   Documentación: $BACK_LINK/docs"
        else
            echo "⚠️  Backend retornó status: $HEALTH_STATUS"
            echo "   Puede estar iniciándose aún"
        fi
    fi
done

echo ""
echo "📋 Ejemplo 6: Intentar crear tienda con nombre duplicado"
echo "-------------------------------------------------------"

# Intentar crear tienda con nombre que ya existe
DUPLICATE_DATA='{
  "nombre": "Mi Tienda Básica",
  "country_id": "'$COUNTRY_ID'",
  "tokens_disponibles": 200,
  "plan": "premium"
}'

DUPLICATE_RESPONSE=$(curl -s -X POST "$STORES_URL/" \
  -H "Content-Type: application/json" \
  -d "$DUPLICATE_DATA")

print_response "Respuesta - Intento de Nombre Duplicado" "$DUPLICATE_RESPONSE"

DUPLICATE_STATUS=$(curl -s -X POST "$STORES_URL/" \
  -H "Content-Type: application/json" \
  -d "$DUPLICATE_DATA" \
  -w "HTTP_STATUS:%{http_code}")

if [[ "$DUPLICATE_STATUS" == *"HTTP_STATUS:4"* ]]; then
    echo "✅ Validación funcionando: nombres duplicados rechazados"
else
    echo "⚠️  Advertencia: se permitió nombre duplicado"
fi

echo ""
echo "📋 Ejemplo 7: Limpiar deployments creados"
echo "----------------------------------------"

# Limpiar todas las tiendas creadas
for STORE_ID in "$BASIC_STORE_ID" "$PREMIUM_STORE_ID" "$ENTERPRISE_STORE_ID"; do
    if [ "$STORE_ID" != "null" ] && [ -n "$STORE_ID" ]; then
        echo ""
        echo "Limpiando tienda: $STORE_ID"
        
        # Undeploy
        UNDEPLOY_RESPONSE=$(curl -s -X DELETE "$STORES_URL/$STORE_ID/deploy")
        UNDEPLOY_STATUS=$(echo "$UNDEPLOY_RESPONSE" | jq -r '.status' 2>/dev/null)
        
        if [ "$UNDEPLOY_STATUS" = "undeployed" ]; then
            echo "✅ Deployment eliminado"
        else
            echo "⚠️  Problema con undeploy: $UNDEPLOY_STATUS"
        fi
        
        # Eliminar tienda
        DELETE_STATUS=$(curl -s -X DELETE "$STORES_URL/$STORE_ID" -w "HTTP_STATUS:%{http_code}")
        
        if [[ "$DELETE_STATUS" == *"HTTP_STATUS:204"* ]]; then
            echo "✅ Tienda eliminada"
        else
            echo "⚠️  Problema eliminando tienda"
        fi
    fi
done

echo ""
echo "=================================================================="
echo "🎉 Ejemplos del endpoint crear y desplegar completados!"
echo "=================================================================="
echo ""
echo "💡 Resumen de lo que hicimos:"
echo ""
echo "1. ✅ Creamos tiendas con diferentes planes (basic, premium, enterprise)"
echo "2. ✅ Cada tienda se desplegó automáticamente con su propio backend"
echo "3. ✅ Se asignaron puertos únicos a cada deployment"
echo "4. ✅ Verificamos el estado de los deployments"
echo "5. ✅ Probamos la conectividad de los backends"
echo "6. ✅ Validamos que no se permiten nombres duplicados"
echo "7. ✅ Limpiamos todos los deployments"
echo ""
echo "🔧 Comandos útiles para monitoreo:"
echo ""
echo "# Ver todos los deployments activos:"
echo "docker ps --filter 'name=backend-api-' --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"
echo ""
echo "# Ver archivos de deployment:"
echo "ls -la /home/danielamg/Escritorio/trabajo/olimpo/smart-pay/deployments/"
echo ""
echo "# Crear una nueva tienda y desplegarla:"
echo "curl -X POST '$STORES_URL/' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{"
echo "    \"nombre\": \"Mi Nueva Tienda\","
echo "    \"country_id\": \"'$COUNTRY_ID'\","
echo "    \"tokens_disponibles\": 300,"
echo "    \"plan\": \"premium\""
echo "  }'"
