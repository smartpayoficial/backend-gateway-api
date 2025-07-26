#!/bin/bash

# Script para configurar Traefik en el VPS de SmartPay con puertos garantizados disponibles
# Autor: SmartPay Team
# Fecha: $(date +%Y-%m-%d)

# Colores para mensajes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Puertos personalizados que deberían estar disponibles
HTTP_PORT=7080
HTTPS_PORT=7443
DASHBOARD_PORT=7000

echo -e "${YELLOW}Iniciando configuración de Traefik para SmartPay VPS (puertos personalizados)...${NC}"

# Crear directorios necesarios
echo "Creando estructura de directorios..."
mkdir -p /home/smartpayvps/traefik/data

# Crear archivos de configuración
echo "Creando archivos de configuración..."

# traefik.yml - Usando puertos personalizados
cat > /home/smartpayvps/traefik/data/traefik.yml << 'EOT'
api:
  dashboard: true
  insecure: true

entryPoints:
  web:
    address: ":7080"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
  websecure:
    address: ":7443"
    http:
      tls:
        certResolver: letsencrypt

providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false
    network: traefik-public
  file:
    filename: /config.yml

certificatesResolvers:
  letsencrypt:
    acme:
      email: admin@smartpay-oficial.com
      storage: acme.json
      httpChallenge:
        entryPoint: web

log:
  level: INFO
EOT

# config.yml
cat > /home/smartpayvps/traefik/data/config.yml << 'EOT'
http:
  routers:
    dashboard:
      rule: "Host(`traefik.smartpay-oficial.com`)"
      service: "api@internal"
      tls:
        certResolver: letsencrypt
      middlewares:
        - auth

  middlewares:
    auth:
      basicAuth:
        users:
          - "admin:$apr1$ruca84Hq$mbjdMZpxBhuM1Zh4POr4d1"
EOT

# Crear archivo acme.json con permisos correctos
touch /home/smartpayvps/traefik/data/acme.json
chmod 600 /home/smartpayvps/traefik/data/acme.json

# docker-compose.yml para Traefik con puertos personalizados
cat > /home/smartpayvps/traefik/docker-compose.yml << 'EOT'
version: '3'

services:
  traefik:
    image: traefik:v2.10
    container_name: traefik
    restart: unless-stopped
    security_opt:
      - no-new-privileges:true
    ports:
      - "7080:7080"
      - "7443:7443"
      - "7000:8080"
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./data/traefik.yml:/traefik.yml:ro
      - ./data/acme.json:/acme.json
      - ./data/config.yml:/config.yml:ro
    networks:
      - traefik-public
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.dashboard.rule=Host(`traefik.smartpay-oficial.com`)"
      - "traefik.http.routers.dashboard.service=api@internal"
      - "traefik.http.routers.dashboard.entrypoints=websecure"
      - "traefik.http.routers.dashboard.tls.certresolver=letsencrypt"
      - "traefik.http.middlewares.auth.basicauth.users=admin:$$apr1$$ruca84Hq$$mbjdMZpxBhuM1Zh4POr4d1"
      - "traefik.http.routers.dashboard.middlewares=auth"

networks:
  traefik-public:
    external: true
EOT

# Crear la red de Docker para Traefik
echo "Creando red Docker para Traefik..."
docker network create traefik-public || true

# Iniciar Traefik
echo "Iniciando Traefik..."
cd /home/smartpayvps/traefik
docker-compose up -d

# Verificar que Traefik está corriendo
if [ $(docker ps | grep -c traefik) -eq 1 ]; then
    echo -e "${GREEN}Traefik se ha instalado y configurado correctamente.${NC}"
    echo -e "${GREEN}Dashboard disponible en: http://traefik.smartpay-oficial.com:7000${NC}"
    echo -e "${GREEN}Usuario: admin${NC}"
    echo -e "${GREEN}Contraseña: smartpay${NC}"
    echo ""
    echo -e "${YELLOW}IMPORTANTE: Configuración de puertos${NC}"
    echo "Traefik está configurado para usar los siguientes puertos personalizados:"
    echo "- HTTP: 7080 (en lugar de 80)"
    echo "- HTTPS: 7443 (en lugar de 443)"
    echo "- Dashboard: 7000 (en lugar de 8080)"
    
    # Crear script para actualizar el servicio de deployment
    cat > /home/smartpayvps/update_deployment_service.sh << 'EOTPY'
#!/bin/bash

# Script para actualizar el servicio de deployment para usar los puertos personalizados de Traefik
echo "Actualizando el servicio de deployment para usar los puertos personalizados de Traefik..."

# Crear archivo temporal con los cambios
cat > /tmp/deployment_traefik_update.py << 'PYCODE'
import os
import sys

# Archivo a modificar
deployment_file = '/home/smartpayvps/backend-gateway-api/app/services/deployment.py'

# Verificar que el archivo existe
if not os.path.exists(deployment_file):
    print(f"Error: El archivo {deployment_file} no existe")
    sys.exit(1)

# Leer el contenido actual
with open(deployment_file, 'r') as f:
    content = f.read()

# Modificar las etiquetas de Traefik para usar los puertos personalizados
updated_content = content.replace(
    '"traefik.http.routers.{store_name}.entrypoints=https"',
    '"traefik.http.routers.{store_name}.entrypoints=websecure"'
)

# Guardar los cambios
with open(deployment_file, 'w') as f:
    f.write(updated_content)

print("Servicio de deployment actualizado correctamente para usar los puertos personalizados de Traefik")
PYCODE

# Ejecutar el script Python
python3 /tmp/deployment_traefik_update.py

# Eliminar el archivo temporal
rm /tmp/deployment_traefik_update.py

echo "Actualización completada"
EOTPY

    chmod +x /home/smartpayvps/update_deployment_service.sh
    
    echo ""
    echo -e "${YELLOW}PRÓXIMOS PASOS:${NC}"
    echo "1. Ejecutar el script de actualización del servicio de deployment:"
    echo "   sudo /home/smartpayvps/update_deployment_service.sh"
    echo "2. Los nuevos deployments de tiendas ya utilizarán Traefik automáticamente"
    echo "3. Para tiendas existentes, necesitará redeployarlas para usar Traefik"
else
    echo -e "${RED}Error: Traefik no se ha iniciado correctamente.${NC}"
    echo "Revise los logs con: docker logs traefik"
fi

echo ""
echo -e "${YELLOW}IMPORTANTE: Configuración DNS${NC}"
echo "Asegúrese de configurar los siguientes registros DNS en su proveedor:"
echo "1. Registro A para *.smartpay-oficial.com apuntando a la IP del VPS"
echo "2. Registro A específico para traefik.smartpay-oficial.com apuntando a la IP del VPS"
echo ""
echo -e "${YELLOW}NOTA IMPORTANTE:${NC}"
echo "Debido a que Traefik está usando puertos no estándar (7080 y 7443),"
echo "necesitará configurar un proxy inverso adicional (como Apache o Nginx) para redirigir"
echo "el tráfico de los puertos estándar (80 y 443) a los puertos de Traefik."
echo ""

# Crear archivo de configuración para Apache
cat > /home/smartpayvps/apache_traefik_proxy.conf << 'EOTAPACHE'
# Configuración de proxy inverso para Apache
# Colocar en /etc/apache2/sites-available/traefik-proxy.conf

<VirtualHost *:80>
    ServerName smartpay-oficial.com
    ServerAlias *.smartpay-oficial.com
    
    ProxyPreserveHost On
    ProxyPass / http://localhost:7080/
    ProxyPassReverse / http://localhost:7080/
    
    ErrorLog ${APACHE_LOG_DIR}/traefik-proxy-error.log
    CustomLog ${APACHE_LOG_DIR}/traefik-proxy-access.log combined
</VirtualHost>

<VirtualHost *:443>
    ServerName smartpay-oficial.com
    ServerAlias *.smartpay-oficial.com
    
    ProxyPreserveHost On
    ProxyPass / https://localhost:7443/
    ProxyPassReverse / https://localhost:7443/
    
    SSLEngine on
    SSLCertificateFile /etc/ssl/smartpay/fullchain.pem
    SSLCertificateKeyFile /etc/ssl/smartpay/smartpay-oficial.com-PrivateKey.pem
    
    ErrorLog ${APACHE_LOG_DIR}/traefik-proxy-ssl-error.log
    CustomLog ${APACHE_LOG_DIR}/traefik-proxy-ssl-access.log combined
</VirtualHost>
EOTAPACHE

echo -e "${YELLOW}CONFIGURACIÓN DE APACHE:${NC}"
echo "Se ha creado un archivo de configuración para Apache en:"
echo "/home/smartpayvps/apache_traefik_proxy.conf"
echo ""
echo "Para configurar Apache como proxy inverso para Traefik, ejecute:"
echo "sudo cp /home/smartpayvps/apache_traefik_proxy.conf /etc/apache2/sites-available/traefik-proxy.conf"
echo "sudo a2enmod proxy proxy_http proxy_wstunnel ssl"
echo "sudo a2ensite traefik-proxy"
echo "sudo systemctl restart apache2"
echo ""
