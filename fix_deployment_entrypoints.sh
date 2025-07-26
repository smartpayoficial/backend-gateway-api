#!/bin/bash

# Script para corregir los entrypoints en el archivo deployment.py
# Este script cambia "https" por "websecure" en las etiquetas de Traefik

echo "Corrigiendo entrypoints en el archivo deployment.py..."

# Ruta al archivo deployment.py
DEPLOYMENT_FILE="/home/smartpayvps/backend-gateway-api/app/services/deployment.py"

# Hacer una copia de seguridad
cp "$DEPLOYMENT_FILE" "${DEPLOYMENT_FILE}.bak"
echo "Copia de seguridad creada en ${DEPLOYMENT_FILE}.bak"

# Reemplazar "entrypoints=https" por "entrypoints=websecure"
sed -i 's/entrypoints=https/entrypoints=websecure/g' "$DEPLOYMENT_FILE"

echo "Entrypoints corregidos en $DEPLOYMENT_FILE"

# Verificar los cambios
echo "Verificando cambios..."
grep -n "entrypoints=" "$DEPLOYMENT_FILE"

echo "Ahora debe reiniciar el servicio de API para aplicar los cambios"
echo "Y luego intentar crear una nueva tienda"
