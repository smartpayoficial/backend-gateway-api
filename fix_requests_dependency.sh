#!/bin/bash

echo "=== ARREGLANDO DEPENDENCIA REQUESTS FALTANTE ==="
echo "Fecha: $(date)"
echo ""

echo "1. Deteniendo servicios actuales..."
docker-compose -f docker/Docker-compose.dev.yml down
echo ""

echo "2. Verificando que requests esté en requirements.txt..."
grep -n "requests" requirements.txt && echo "   ✅ requests encontrado en requirements.txt" || echo "   ❌ requests NO encontrado"
echo ""

echo "3. Reconstruyendo imagen con todas las dependencias..."
docker-compose -f docker/Docker-compose.dev.yml build --no-cache
echo ""

echo "4. Iniciando servicios..."
docker-compose -f docker/Docker-compose.dev.yml up -d
echo ""

echo "5. Esperando que los servicios inicien..."
sleep 15

echo "6. Verificando estado de contenedores..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "7. Verificando que requests esté instalado en el contenedor..."
docker exec backend-api python -c "import requests; print(f'requests version: {requests.__version__}')" 2>/dev/null && echo "   ✅ requests instalado correctamente" || echo "   ❌ requests no disponible"
echo ""

echo "8. Verificando logs del backend-api..."
docker logs backend-api --tail 10
echo ""

echo "9. Probando conectividad..."
echo "   HTTP puerto 8000:"
curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:8000/ || echo "   ❌ Falló"
echo ""

echo "=== CORRECCIÓN COMPLETADA ==="
echo "Si todo salió bien, el backend debería estar funcionando en:"
echo "  - http://localhost:8000 (desarrollo)"
echo "  - http://localhost:8000/docs (Swagger UI)"
