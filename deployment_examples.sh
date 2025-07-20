#!/bin/bash

# Script de ejemplos para el sistema de deployment automático
# Este script muestra cómo usar los endpoints de deployment con curl

BASE_URL="http://localhost:8000/api/v1"
STORES_URL="$BASE_URL/stores"

echo "🚀 Ejemplos de uso del sistema de deployment automático"
echo "======================================================="

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
echo "📋 Ejemplo 1: Crear una tienda de prueba"
echo "----------------------------------------"

# Obtener un country_id válido
COUNTRY_ID=$(get_first_country)
if [ "$COUNTRY_ID" = "null" ] || [ -z "$COUNTRY_ID" ]; then
    echo "❌ Error: No se pudo obtener un país válido"
    echo "Asegúrate de que hay países en la base de datos"
    exit 1
fi

echo "✅ Usando country_id: $COUNTRY_ID"

# Crear tienda de prueba
STORE_DATA='{
  "nombre": "Tienda Ejemplo Deployment",
  "country_id": "'$COUNTRY_ID'",
  "tokens_disponibles": 100,
  "plan": "premium"
}'

echo ""
echo "Creando tienda con datos:"
echo "$STORE_DATA" | jq .

CREATE_RESPONSE=$(curl -s -X POST "$STORES_URL" \
  -H "Content-Type: application/json" \
  -d "$STORE_DATA")

print_response "Respuesta de creación de tienda" "$CREATE_RESPONSE"

# Extraer el store_id
STORE_ID=$(echo "$CREATE_RESPONSE" | jq -r '.id' 2>/dev/null)

if [ "$STORE_ID" = "null" ] || [ -z "$STORE_ID" ]; then
    echo "❌ Error: No se pudo crear la tienda o extraer el ID"
    exit 1
fi

echo "✅ Tienda creada con ID: $STORE_ID"

echo ""
echo "📋 Ejemplo 2: Verificar estado inicial del deployment"
echo "----------------------------------------------------"

STATUS_RESPONSE=$(curl -s -X GET "$STORES_URL/$STORE_ID/deploy/status")
print_response "Estado inicial del deployment" "$STATUS_RESPONSE"

echo ""
echo "📋 Ejemplo 3: Realizar deployment de la tienda"
echo "----------------------------------------------"

echo "Iniciando deployment..."
DEPLOY_RESPONSE=$(curl -s -X POST "$STORES_URL/$STORE_ID/deploy")
print_response "Respuesta del deployment" "$DEPLOY_RESPONSE"

# Verificar si el deployment fue exitoso
DEPLOY_STATUS=$(echo "$DEPLOY_RESPONSE" | jq -r '.status' 2>/dev/null)
BACK_LINK=$(echo "$DEPLOY_RESPONSE" | jq -r '.back_link' 2>/dev/null)

if [ "$DEPLOY_STATUS" = "deployed" ] && [ "$BACK_LINK" != "null" ]; then
    echo "✅ Deployment completado exitosamente!"
    echo "   Backend URL: $BACK_LINK"
    
    # Extraer puertos para mostrar información útil
    BACKEND_PORT=$(echo "$DEPLOY_RESPONSE" | jq -r '.ports.backend_port' 2>/dev/null)
    WEBSOCKET_PORT=$(echo "$DEPLOY_RESPONSE" | jq -r '.ports.websocket_port' 2>/dev/null)
    DB_PORT=$(echo "$DEPLOY_RESPONSE" | jq -r '.ports.db_port' 2>/dev/null)
    
    echo "   Puertos asignados:"
    echo "     - Backend: $BACKEND_PORT"
    echo "     - WebSocket: $WEBSOCKET_PORT"
    echo "     - DB: $DB_PORT"
else
    echo "⚠️  El deployment puede no haber sido completamente exitoso"
fi

echo ""
echo "📋 Ejemplo 4: Verificar estado después del deployment"
echo "----------------------------------------------------"

echo "Esperando 5 segundos para que los servicios se inicien..."
sleep 5

STATUS_RESPONSE=$(curl -s -X GET "$STORES_URL/$STORE_ID/deploy/status")
print_response "Estado después del deployment" "$STATUS_RESPONSE"

echo ""
echo "📋 Ejemplo 5: Verificar que la tienda fue actualizada"
echo "----------------------------------------------------"

STORE_RESPONSE=$(curl -s -X GET "$STORES_URL/$STORE_ID")
print_response "Tienda actualizada con links" "$STORE_RESPONSE"

echo ""
echo "📋 Ejemplo 6: Intentar deployment duplicado"
echo "------------------------------------------"

DUPLICATE_RESPONSE=$(curl -s -X POST "$STORES_URL/$STORE_ID/deploy")
print_response "Respuesta de deployment duplicado" "$DUPLICATE_RESPONSE"

echo ""
echo "📋 Ejemplo 7: Probar el backend desplegado (opcional)"
echo "----------------------------------------------------"

if [ "$BACK_LINK" != "null" ] && [ -n "$BACK_LINK" ]; then
    echo "Probando conectividad al backend desplegado..."
    
    # Intentar acceder a la documentación del backend desplegado
    HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BACK_LINK/docs" --connect-timeout 10)
    
    if [ "$HEALTH_STATUS" = "200" ]; then
        echo "✅ Backend desplegado está respondiendo correctamente"
        echo "   Documentación disponible en: $BACK_LINK/docs"
    else
        echo "⚠️  Backend desplegado retornó status: $HEALTH_STATUS"
        echo "   Esto es normal si los contenedores aún se están iniciando"
    fi
else
    echo "⚠️  No hay back_link disponible para probar"
fi

echo ""
echo "📋 Ejemplo 8: Eliminar el deployment"
echo "-----------------------------------"

echo "Eliminando deployment..."
UNDEPLOY_RESPONSE=$(curl -s -X DELETE "$STORES_URL/$STORE_ID/deploy")
print_response "Respuesta del undeploy" "$UNDEPLOY_RESPONSE"

echo ""
echo "📋 Ejemplo 9: Verificar estado final"
echo "-----------------------------------"

FINAL_STATUS_RESPONSE=$(curl -s -X GET "$STORES_URL/$STORE_ID/deploy/status")
print_response "Estado final del deployment" "$FINAL_STATUS_RESPONSE"

echo ""
echo "📋 Ejemplo 10: Limpiar - Eliminar tienda de prueba"
echo "-------------------------------------------------"

DELETE_RESPONSE=$(curl -s -X DELETE "$STORES_URL/$STORE_ID" -w "HTTP_STATUS:%{http_code}")

if [[ "$DELETE_RESPONSE" == *"HTTP_STATUS:204"* ]]; then
    echo "✅ Tienda de prueba eliminada exitosamente"
else
    echo "⚠️  Respuesta de eliminación: $DELETE_RESPONSE"
fi

echo ""
echo "======================================================="
echo "🎉 Ejemplos completados!"
echo "======================================================="
echo ""
echo "💡 Comandos útiles para monitoreo:"
echo ""
echo "# Ver contenedores de deployments activos:"
echo "docker ps --filter 'name=backend-api-' --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"
echo ""
echo "# Ver logs de un deployment específico:"
echo "docker logs backend-api-{store_id}"
echo ""
echo "# Detener manualmente un deployment:"
echo "docker stop backend-api-{store_id}"
echo ""
echo "# Ver archivos de deployment:"
echo "ls -la /home/danielamg/Escritorio/trabajo/olimpo/smart-pay/deployments/"
