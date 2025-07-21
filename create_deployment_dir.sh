#!/bin/bash

echo "=== CREANDO DIRECTORIO DE DEPLOYMENTS Y REINICIANDO SERVICIOS ==="
echo "Fecha: $(date)"
echo ""

echo "1. Creando directorio de deployments..."
sudo mkdir -p /home/smartpayvps/deployments
sudo chown smartpayvps:smartpayvps /home/smartpayvps/deployments
echo "   ✅ Directorio /home/smartpayvps/deployments creado"
echo ""

echo "2. Verificando permisos..."
ls -la /home/smartpayvps/deployments
echo ""

echo "3. Verificando estado actual de contenedores..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "4. Reiniciando servicios para aplicar cambios..."
echo "   Deteniendo servicios..."
docker-compose -f docker/Docker-compose.vps.yml down

echo "   Esperando 5 segundos..."
sleep 5

echo "   Iniciando servicios..."
docker-compose -f docker/Docker-compose.vps.yml up -d

echo ""
echo "5. Verificando servicios reiniciados..."
sleep 10
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "6. Verificando logs del backend-api..."
echo "   Últimas 20 líneas de logs:"
docker logs backend-api --tail 20

echo ""
echo "=== PROCESO COMPLETADO ==="
echo "Los cambios en deployment.py ahora deberían estar activos."
echo "Las rutas configuradas son:"
echo "  - BASE_BACKEND_PATH: /home/smartpayvps/backend-gateway-api"
echo "  - BASE_DB_PATH: /home/smartpayvps/db-smartpay"  
echo "  - DEPLOYMENT_BASE_PATH: /home/smartpayvps/deployments"
