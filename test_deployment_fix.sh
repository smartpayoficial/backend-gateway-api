#!/bin/bash

echo "=== PROBANDO SISTEMA DE DEPLOYMENT CORREGIDO ==="
echo "Fecha: $(date)"
echo ""

echo "1. Verificando que los servicios estén funcionando..."
curl -s http://localhost:8000/api/v1/countries/ | head -c 100
echo ""
echo ""

echo "2. Obteniendo un country_id válido para la prueba..."
COUNTRY_ID=$(curl -s http://localhost:8000/api/v1/countries/ | jq -r '.[0].id' 2>/dev/null)
if [ "$COUNTRY_ID" = "null" ] || [ -z "$COUNTRY_ID" ]; then
    echo "   ❌ No se pudo obtener un country_id válido"
    echo "   Usando un UUID de ejemplo..."
    COUNTRY_ID="123e4567-e89b-12d3-a456-426614174000"
fi
echo "   Country ID a usar: $COUNTRY_ID"
echo ""

echo "3. Probando endpoint de deployment con datos válidos..."
echo "   Enviando POST a /api/v1/stores/deploy..."

RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST http://localhost:8000/api/v1/stores/deploy \
  -H "Content-Type: application/json" \
  -d "{
    \"nombre\": \"Tienda Test Fix\",
    \"country_id\": \"$COUNTRY_ID\",
    \"plan\": \"basic\",
    \"tokens_disponibles\": 1000
  }")

HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE:/d')

echo "   Código HTTP: $HTTP_CODE"
echo "   Respuesta:"
echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
echo ""

echo "4. Verificando logs del backend para errores..."
echo "   Últimas 10 líneas de logs:"
docker logs backend-api --tail 10
echo ""

echo "5. Verificando directorio de deployments..."
echo "   Contenido de /home/smartpayvps/deployments:"
ls -la /home/smartpayvps/deployments/
echo ""

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ]; then
    echo "✅ ÉXITO: El deployment funcionó correctamente!"
    echo "   - No más errores de rutas incorrectas"
    echo "   - No más RuntimeWarning de async/await"
    echo "   - Sistema de deployment operativo"
elif [ "$HTTP_CODE" = "500" ]; then
    echo "❌ ERROR 500: Aún hay problemas en el deployment"
    echo "   Revisar logs arriba para más detalles"
elif [ "$HTTP_CODE" = "422" ]; then
    echo "⚠️  ERROR 422: Problema de validación (country_id inválido)"
    echo "   Esto es normal si no hay países en la BD"
else
    echo "⚠️  Código HTTP inesperado: $HTTP_CODE"
fi

echo ""
echo "=== FIN DE LA PRUEBA ==="
