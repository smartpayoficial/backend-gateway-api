#!/bin/bash

echo "=== REINICIANDO EN MODO DESARROLLO (HTTP SIN SSL) ==="
echo "Fecha: $(date)"
echo ""

echo "1. Deteniendo servicios..."
docker-compose -f docker/Docker-compose.dev.yml down
echo ""

echo "2. Iniciando servicios sin SSL..."
docker-compose -f docker/Docker-compose.dev.yml up -d
echo ""

echo "3. Esperando que los servicios inicien..."
sleep 10

echo "4. Verificando estado..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep backend-api
echo ""

echo "5. Verificando logs..."
docker logs backend-api --tail 10
echo ""

echo "6. Probando conectividad HTTP..."
curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:8000/ && echo "   ✅ HTTP funcionando" || echo "   ❌ HTTP falló"
echo ""

echo "7. Verificando que requests esté disponible..."
docker exec backend-api python -c "import requests; print('✅ requests disponible')" 2>/dev/null || echo "   ❌ requests no disponible"
echo ""

echo "=== DESARROLLO HTTP LISTO ==="
echo "Backend disponible en:"
echo "  - http://localhost:8000 (API)"
echo "  - http://localhost:8000/docs (Swagger UI)"
echo "  - http://localhost:8001 (WebSocket)"
