#!/bin/bash

echo "=== DIAGNÓSTICO DE PROBLEMA HTTPS/HTTP ==="
echo "Fecha: $(date)"
echo ""

echo "1. Estado de contenedores..."
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.Image}}"
echo ""

echo "2. Verificando si el contenedor backend-api está corriendo..."
if docker ps | grep -q "backend-api"; then
    echo "   ✅ Contenedor backend-api está corriendo"
    
    echo "3. Logs del backend-api (últimas 20 líneas)..."
    docker logs backend-api --tail 20
    echo ""
    
    echo "4. Verificando certificados SSL dentro del contenedor..."
    echo "   /etc/ssl/smartpay/fullchain.pem:"
    docker exec backend-api ls -la /etc/ssl/smartpay/fullchain.pem 2>/dev/null || echo "   ❌ No encontrado"
    echo "   /etc/ssl/smartpay/smartpay-oficial.com-PrivateKey.pem:"
    docker exec backend-api ls -la /etc/ssl/smartpay/smartpay-oficial.com-PrivateKey.pem 2>/dev/null || echo "   ❌ No encontrado"
    echo ""
    
    echo "5. Verificando puertos dentro del contenedor..."
    docker exec backend-api netstat -tlnp 2>/dev/null | grep -E ":(443|8000|8001)" || echo "   ❌ No hay puertos escuchando"
    echo ""
    
    echo "6. Verificando proceso uvicorn..."
    docker exec backend-api ps aux | grep uvicorn || echo "   ❌ Proceso uvicorn no encontrado"
    echo ""
    
else
    echo "   ❌ Contenedor backend-api NO está corriendo"
    echo ""
    echo "3. Logs del contenedor (si existe)..."
    docker logs backend-api --tail 30 2>/dev/null || echo "   No hay logs disponibles"
    echo ""
fi

echo "7. Verificando puertos en el host..."
echo "   Puerto 443:"
netstat -tlnp | grep :443 || echo "   ❌ Puerto 443 no está en uso"
echo "   Puerto 8000:"
netstat -tlnp | grep :8000 || echo "   ❌ Puerto 8000 no está en uso"
echo "   Puerto 8001:"
netstat -tlnp | grep :8001 || echo "   ❌ Puerto 8001 no está en uso"
echo ""

echo "8. Verificando certificados en el host..."
echo "   /etc/ssl/smartpay/fullchain.pem: $([ -f '/etc/ssl/smartpay/fullchain.pem' ] && echo 'EXISTE' || echo 'NO EXISTE')"
echo "   /etc/ssl/smartpay/smartpay-oficial.com-PrivateKey.pem: $([ -f '/etc/ssl/smartpay/smartpay-oficial.com-PrivateKey.pem' ] && echo 'EXISTE' || echo 'NO EXISTE')"
echo ""

echo "9. Intentando conexiones..."
echo "   HTTP local (puerto 8000):"
curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:8000/ 2>/dev/null || echo "   ❌ Conexión falló"
echo "   HTTPS local (puerto 443):"
curl -k -s -o /dev/null -w "Status: %{http_code}\n" https://localhost:443/ 2>/dev/null || echo "   ❌ Conexión falló"
echo "   HTTPS dominio:"
curl -k -s -o /dev/null -w "Status: %{http_code}\n" https://smartpay-oficial.com/ 2>/dev/null || echo "   ❌ Conexión falló"
echo ""

echo "=== FIN DEL DIAGNÓSTICO ==="
