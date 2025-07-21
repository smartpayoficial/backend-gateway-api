#!/bin/bash

echo "=== RECONSTRUYENDO IMAGEN CON DOCKER Y REINICIANDO ==="
echo "Fecha: $(date)"
echo ""

echo "1. Deteniendo servicios actuales..."
docker-compose -f docker/Docker-compose.vps.yml down
echo ""

echo "2. Eliminando imagen anterior para forzar rebuild..."
docker rmi backend-gateway-api-api 2>/dev/null || echo "   Imagen no encontrada, continuando..."
echo ""

echo "3. Reconstruyendo imagen con Docker CLI incluido..."
docker-compose -f docker/Docker-compose.vps.yml build --no-cache
echo ""

echo "4. Iniciando servicios con imagen reconstruida..."
docker-compose -f docker/Docker-compose.vps.yml up -d
echo ""

echo "5. Esperando que los servicios se inicien..."
sleep 20

echo "6. Verificando que Docker esté disponible en el contenedor..."
echo "   Probando 'docker --version' dentro del contenedor:"
docker exec backend-api docker --version 2>/dev/null || echo "   ❌ Docker no disponible en el contenedor"

echo "   Probando 'docker-compose --version' dentro del contenedor:"
docker exec backend-api docker-compose --version 2>/dev/null || echo "   ❌ docker-compose no disponible en el contenedor"
echo ""

echo "7. Verificando servicios..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "8. Verificando logs iniciales..."
echo "   Últimas 10 líneas de logs del backend:"
docker logs backend-api --tail 10
echo ""

echo "=== RECONSTRUCCIÓN COMPLETADA ==="
echo "La imagen ahora debería tener Docker CLI disponible."
echo "Prueba el deployment nuevamente para verificar que funciona."
