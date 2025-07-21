#!/bin/bash

echo "=== APLICANDO FIX FINAL DE VOLÚMENES Y REINICIANDO ==="
echo "Fecha: $(date)"
echo ""

echo "1. Verificando que los directorios existen en el host..."
echo "   /home/smartpayvps/backend-gateway-api: $([ -d '/home/smartpayvps/backend-gateway-api' ] && echo 'EXISTE' || echo 'NO EXISTE')"
echo "   /home/smartpayvps/db-smartpay: $([ -d '/home/smartpayvps/db-smartpay' ] && echo 'EXISTE' || echo 'NO EXISTE')"
echo "   /home/smartpayvps/deployments: $([ -d '/home/smartpayvps/deployments' ] && echo 'EXISTE' || echo 'NO EXISTE')"
echo ""

echo "2. Deteniendo servicios actuales..."
docker-compose -f docker/Docker-compose.vps.yml down
echo ""

echo "3. Esperando 5 segundos..."
sleep 5

echo "4. Iniciando servicios con nueva configuración de volúmenes..."
docker-compose -f docker/Docker-compose.vps.yml up -d
echo ""

echo "5. Esperando que los servicios se inicien..."
sleep 15

echo "6. Verificando servicios..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "7. Verificando montajes dentro del contenedor..."
echo "   Ejecutando comando dentro del contenedor para verificar rutas:"
docker exec backend-api ls -la /host/smartpayvps/ 2>/dev/null || echo "   Error accediendo al contenedor o ruta no montada"
echo ""

echo "8. Verificando logs iniciales..."
echo "   Últimas 10 líneas de logs del backend:"
docker logs backend-api --tail 10
echo ""

echo "=== CONFIGURACIÓN FINAL ==="
echo "Volumen montado: /home/smartpayvps -> /host/smartpayvps"
echo "Rutas esperadas en el contenedor:"
echo "  - /host/smartpayvps/backend-gateway-api"
echo "  - /host/smartpayvps/db-smartpay"  
echo "  - /host/smartpayvps/deployments"
echo ""
echo "¡Ahora prueba el deployment nuevamente!"
