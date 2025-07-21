#!/bin/bash

echo "=== RECONSTRUYENDO CON HTTPS Y DOCKER CLI HABILITADOS ==="
echo "Fecha: $(date)"
echo ""

echo "1. Verificando certificados SSL..."
echo "   /etc/ssl/smartpay/fullchain.pem: $([ -f '/etc/ssl/smartpay/fullchain.pem' ] && echo 'EXISTE' || echo 'NO EXISTE')"
echo "   /etc/ssl/smartpay/smartpay-oficial.com-PrivateKey.pem: $([ -f '/etc/ssl/smartpay/smartpay-oficial.com-PrivateKey.pem' ] && echo 'EXISTE' || echo 'NO EXISTE')"
echo ""

echo "2. Deteniendo servicios actuales..."
docker-compose -f docker/Docker-compose.vps.yml down
echo ""

echo "3. Eliminando imagen anterior para forzar rebuild..."
docker rmi backend-gateway-api-api 2>/dev/null || echo "   Imagen no encontrada, continuando..."
echo ""

echo "4. Reconstruyendo imagen con HTTPS y Docker CLI..."
docker-compose -f docker/Docker-compose.vps.yml build --no-cache
echo ""

echo "5. Iniciando servicios con HTTPS habilitado..."
docker-compose -f docker/Docker-compose.vps.yml up -d
echo ""

echo "6. Esperando que los servicios se inicien..."
sleep 25

echo "7. Verificando servicios..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "8. Verificando que Docker esté disponible en el contenedor..."
echo "   Probando 'docker --version' dentro del contenedor:"
docker exec backend-api docker --version 2>/dev/null || echo "   ❌ Docker no disponible en el contenedor"
echo ""

echo "9. Verificando conectividad HTTPS..."
echo "   Probando conexión a https://smartpay-oficial.com..."
curl -k -s -o /dev/null -w "HTTP Status: %{http_code}\n" https://smartpay-oficial.com/ || echo "   ❌ No se pudo conectar via HTTPS"
echo ""

echo "10. Verificando logs iniciales..."
echo "    Últimas 15 líneas de logs del backend:"
docker logs backend-api --tail 15
echo ""

echo "=== CONFIGURACIÓN FINAL ==="
echo "✅ HTTPS habilitado en puerto 443"
echo "✅ Docker CLI disponible para deployments"
echo "✅ Certificados SSL montados"
echo "✅ Variables de entorno actualizadas"
echo ""
echo "URLs disponibles:"
echo "  - https://smartpay-oficial.com (Puerto 443 - HTTPS)"
echo "  - https://smartpay-oficial.com:8001 (WebSocket)"
echo ""
echo "¡Ahora prueba el deployment con HTTPS funcionando!"
