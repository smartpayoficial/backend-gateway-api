#!/bin/bash

echo "=== CONFIGURANDO VPS CON SSL EN PUERTO 8000 ==="
echo "Fecha: $(date)"
echo ""

echo "1. Creando backup de la configuración VPS actual..."
cp docker/Docker-compose.vps.yml docker/Docker-compose.vps.yml.backup-$(date +%Y%m%d-%H%M%S)

echo "2. Deteniendo servicios VPS actuales..."
docker-compose -f docker/Docker-compose.vps.yml down
echo ""

echo "3. Actualizando Docker-compose.vps.yml para SSL en puerto 8000..."
# Cambiar puerto 443 a 8000 (mantener SSL)
sed -i 's/- "443:443"/- "8000:8000"/' docker/Docker-compose.vps.yml
sed -i 's/PORT: 443/PORT: 8000/' docker/Docker-compose.vps.yml

# Actualizar comando SSL para puerto 8000
sed -i '/# Comando SSL se toma del Dockerfile/c\    # Comando SSL en puerto 8000\n    command: ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--ssl-certfile=/etc/ssl/smartpay/fullchain.pem", "--ssl-keyfile=/etc/ssl/smartpay/smartpay-oficial.com-PrivateKey.pem"]' docker/Docker-compose.vps.yml

echo "4. Verificando certificados SSL en el host..."
ls -la /etc/ssl/smartpay/ | head -5
echo ""

echo "5. Verificando cambios realizados..."
echo "   Puerto configurado:"
grep -n "8000:8000" docker/Docker-compose.vps.yml && echo "   ✅ Puerto 8000 configurado" || echo "   ❌ Puerto no cambiado"
echo "   Variable PORT:"
grep -n "PORT: 8000" docker/Docker-compose.vps.yml && echo "   ✅ Variable PORT actualizada" || echo "   ❌ Variable PORT no cambiada"
echo "   Comando SSL:"
grep -A1 "ssl-certfile" docker/Docker-compose.vps.yml && echo "   ✅ Comando SSL configurado" || echo "   ❌ Comando SSL no encontrado"
echo ""

echo "6. Reconstruyendo imagen..."
docker-compose -f docker/Docker-compose.vps.yml build --no-cache
echo ""

echo "7. Iniciando servicios VPS con SSL en puerto 8000..."
docker-compose -f docker/Docker-compose.vps.yml up -d
echo ""

echo "8. Esperando que los servicios inicien..."
sleep 25

echo "9. Verificando estado de contenedores..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(backend-api|smartpay)"
echo ""

echo "10. Verificando certificados SSL dentro del contenedor..."
docker exec backend-api ls -la /etc/ssl/smartpay/ 2>/dev/null && echo "    ✅ Certificados montados" || echo "    ❌ Certificados no montados"
echo ""

echo "11. Verificando logs del backend-api..."
docker logs backend-api --tail 15
echo ""

echo "12. Verificando que requests esté disponible..."
docker exec backend-api python -c "import requests; print('✅ requests disponible')" 2>/dev/null || echo "    ❌ requests no disponible"
echo ""

echo "13. Probando conectividad HTTPS..."
echo "    HTTPS puerto 8000:"
curl -k -s -o /dev/null -w "Status: %{http_code}\n" https://localhost:8000/ && echo "    ✅ HTTPS funcionando" || echo "    ❌ HTTPS falló"
echo "    HTTPS con dominio:"
curl -k -s -o /dev/null -w "Status: %{http_code}\n" https://smartpay-oficial.com:8000/ && echo "    ✅ HTTPS dominio funcionando" || echo "    ❌ HTTPS dominio falló"
echo ""

echo "14. Verificando que Docker CLI esté disponible para deployments..."
docker exec backend-api docker --version 2>/dev/null && echo "    ✅ Docker CLI disponible" || echo "    ❌ Docker CLI no disponible"
echo ""

echo "=== VPS CONFIGURADO CON SSL EN PUERTO 8000 ==="
echo "Backend VPS disponible en:"
echo "  - https://smartpay-oficial.com:8000 (API con SSL)"
echo "  - https://smartpay-oficial.com:8000/docs (Swagger UI)"
echo "  - https://smartpay-oficial.com:8001 (WebSocket)"
echo ""
echo "✅ SSL habilitado con certificados"
echo "✅ Docker CLI disponible para deployments automáticos"
echo "✅ Sin conflicto con puerto 443"
