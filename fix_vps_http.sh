#!/bin/bash

echo "=== CONFIGURANDO VPS PARA HTTP SIN SSL (TEMPORAL) ==="
echo "Fecha: $(date)"
echo ""

echo "1. Creando backup de la configuración VPS actual..."
cp docker/Docker-compose.vps.yml docker/Docker-compose.vps.yml.backup-$(date +%Y%m%d-%H%M%S)

echo "2. Deteniendo servicios VPS actuales..."
docker-compose -f docker/Docker-compose.vps.yml down
echo ""

echo "3. Actualizando Docker-compose.vps.yml para HTTP temporal..."
# Cambiar puerto 443 a 8000 y deshabilitar SSL temporalmente
sed -i 's/- "443:443"/- "8000:8000"/' docker/Docker-compose.vps.yml
sed -i 's/PORT: 443/PORT: 8000/' docker/Docker-compose.vps.yml
sed -i 's|https://smartpay-oficial.com:9443/api/v1/google/auth/callback|https://smartpay-oficial.com:8000/api/v1/google/auth/callback|' docker/Docker-compose.vps.yml
sed -i 's|https://smartpay-oficial.com/reset-password|https://smartpay-oficial.com:8000/reset-password|' docker/Docker-compose.vps.yml

# Comentar el montaje de certificados SSL temporalmente
sed -i 's|- /etc/ssl/smartpay:/etc/ssl/smartpay:ro|# - /etc/ssl/smartpay:/etc/ssl/smartpay:ro  # Comentado temporalmente|' docker/Docker-compose.vps.yml

# Agregar comando sin SSL
sed -i '/# Comando SSL se toma del Dockerfile/c\    # Comando HTTP temporal (sin SSL)\n    command: ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]' docker/Docker-compose.vps.yml

echo "4. Verificando cambios realizados..."
echo "   Puerto configurado:"
grep -n "8000:8000" docker/Docker-compose.vps.yml || echo "   ❌ Puerto no cambiado"
echo "   Variable PORT:"
grep -n "PORT: 8000" docker/Docker-compose.vps.yml || echo "   ❌ Variable PORT no cambiada"
echo "   Certificados SSL:"
grep -n "# - /etc/ssl/smartpay" docker/Docker-compose.vps.yml || echo "   ❌ SSL no comentado"
echo ""

echo "5. Reconstruyendo imagen..."
docker-compose -f docker/Docker-compose.vps.yml build --no-cache
echo ""

echo "6. Iniciando servicios VPS en modo HTTP..."
docker-compose -f docker/Docker-compose.vps.yml up -d
echo ""

echo "7. Esperando que los servicios inicien..."
sleep 20

echo "8. Verificando estado de contenedores..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(backend-api|smartpay)"
echo ""

echo "9. Verificando logs del backend-api..."
docker logs backend-api --tail 10
echo ""

echo "10. Verificando que requests esté disponible..."
docker exec backend-api python -c "import requests; print('✅ requests disponible')" 2>/dev/null || echo "    ❌ requests no disponible"
echo ""

echo "11. Probando conectividad..."
echo "    HTTP puerto 8000:"
curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:8000/ && echo "    ✅ HTTP funcionando" || echo "    ❌ HTTP falló"
echo ""

echo "=== VPS CONFIGURADO TEMPORALMENTE PARA HTTP ==="
echo "Backend VPS disponible en:"
echo "  - http://smartpay-oficial.com:8000 (API)"
echo "  - http://smartpay-oficial.com:8000/docs (Swagger UI)"
echo "  - http://smartpay-oficial.com:8001 (WebSocket)"
echo ""
echo "NOTA: Esta es una configuración temporal sin SSL."
echo "Para restaurar SSL, usa: mv docker/Docker-compose.vps.yml.backup-* docker/Docker-compose.vps.yml"
