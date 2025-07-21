#!/bin/bash

echo "=== DIAGNÓSTICO DE RUTAS VPS ==="
echo "Fecha: $(date)"
echo ""

echo "1. Verificando rutas del contenedor:"
echo "   /host/smart-pay/backend-gateway-api: $([ -d '/host/smart-pay/backend-gateway-api' ] && echo 'EXISTE' || echo 'NO EXISTE')"
echo "   /host/smart-pay/db-smartpay: $([ -d '/host/smart-pay/db-smartpay' ] && echo 'EXISTE' || echo 'NO EXISTE')"
echo ""

echo "2. Verificando rutas del VPS:"
echo "   /home/smartpayvps/backend-gateway-api: $([ -d '/home/smartpayvps/backend-gateway-api' ] && echo 'EXISTE' || echo 'NO EXISTE')"
echo "   /home/smartpayvps/db-smartpay: $([ -d '/home/smartpayvps/db-smartpay' ] && echo 'EXISTE' || echo 'NO EXISTE')"
echo "   /home/smartpayvps/deployments: $([ -d '/home/smartpayvps/deployments' ] && echo 'EXISTE' || echo 'NO EXISTE')"
echo ""

echo "3. Listando contenido de /home/smartpayvps/ (si existe):"
if [ -d '/home/smartpayvps' ]; then
    ls -la /home/smartpayvps/
else
    echo "   Directorio /home/smartpayvps no existe"
fi
echo ""

echo "4. Verificando usuario actual y permisos:"
echo "   Usuario actual: $(whoami)"
echo "   Directorio actual: $(pwd)"
echo "   UID: $(id -u)"
echo "   GID: $(id -g)"
echo ""

echo "5. Verificando si estamos en contenedor:"
if [ -f /.dockerenv ]; then
    echo "   ESTAMOS EN CONTENEDOR"
    echo "   Contenido de /.dockerenv:"
    cat /.dockerenv
else
    echo "   NO ESTAMOS EN CONTENEDOR"
fi
echo ""

echo "6. Verificando montajes (si estamos en contenedor):"
if [ -f /.dockerenv ]; then
    echo "   Montajes disponibles:"
    mount | grep -E "(host|smart-pay)" || echo "   No hay montajes relacionados con smart-pay"
fi
echo ""

echo "7. Variables de entorno relevantes:"
env | grep -i smart || echo "   No hay variables de entorno relacionadas con smart"
echo ""

echo "=== FIN DEL DIAGNÓSTICO ==="
