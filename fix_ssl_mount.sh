#!/bin/bash

echo "=== ARREGLANDO MONTAJE DE CERTIFICADOS SSL ==="
echo "Fecha: $(date)"
echo ""

echo "1. Verificando certificados en el host..."
ls -la /etc/ssl/smartpay/
echo ""

echo "2. Deteniendo servicios..."
docker-compose -f docker/Docker-compose.vps.yml down
echo ""

echo "3. Removiendo contenedor problemático..."
docker rm backend-api 2>/dev/null || echo "   Contenedor ya removido"
echo ""

echo "4. Verificando que el volumen SSL esté bien configurado..."
echo "   Contenido actual del docker-compose.vps.yml (sección volumes):"
grep -A 5 -B 5 "ssl/smartpay" docker/Docker-compose.vps.yml
echo ""

echo "5. Iniciando servicios con montaje SSL corregido..."
docker-compose -f docker/Docker-compose.vps.yml up -d
echo ""

echo "6. Esperando que el contenedor inicie..."
sleep 15

echo "7. Verificando estado del contenedor..."
docker ps -a | grep backend-api
echo ""

echo "8. Verificando logs del contenedor..."
echo "   Logs completos:"
docker logs backend-api
echo ""

echo "9. Si el contenedor está corriendo, verificando certificados dentro..."
if docker ps | grep -q "backend-api.*Up"; then
    echo "   ✅ Contenedor corriendo, verificando certificados:"
    docker exec backend-api ls -la /etc/ssl/smartpay/ 2>/dev/null || echo "   ❌ Directorio SSL no montado"
    
    echo "   Verificando proceso uvicorn:"
    docker exec backend-api ps aux | grep uvicorn || echo "   ❌ uvicorn no corriendo"
    
    echo "   Verificando puertos:"
    docker exec backend-api netstat -tlnp | grep -E ":(443|8000)" || echo "   ❌ No hay puertos escuchando"
else
    echo "   ❌ Contenedor no está corriendo"
    echo "   Logs de error:"
    docker logs backend-api --tail 20
fi

echo ""
echo "10. Probando conectividad final..."
echo "    HTTPS:"
curl -k -s -o /dev/null -w "Status: %{http_code}\n" https://localhost:443/ || echo "    ❌ HTTPS falló"

echo ""
echo "=== FIN DE LA CORRECCIÓN ==="
