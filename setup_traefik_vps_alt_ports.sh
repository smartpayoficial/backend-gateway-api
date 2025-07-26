#!/bin/bash

# Script para configurar Traefik en el VPS de SmartPay con puertos alternativos
# Autor: SmartPay Team
# Fecha: $(date +%Y-%m-%d)

# Colores para mensajes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Iniciando configuración de Traefik para SmartPay VPS (puertos alternativos)...${NC}"

# Crear directorios necesarios
echo "Creando estructura de directorios..."
mkdir -p /home/smartpayvps/traefik/data

# Crear archivos de configuración
echo "Creando archivos de configuración..."

# traefik.yml - Usando puertos alternativos
cat > /home/smartpayvps/traefik/data/traefik.yml << 'EOF'
api:
  dashboard: true
  insecure: true

entryPoints:
  web:
    address: ":8081"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
  websecure:
    address: ":8443"
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
EOF

# config.yml
cat > /home/smartpayvps/traefik/data/config.yml << 'EOF'
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
          - "admin:$apr1$ruca84Hq$mbjdMZpxBhuM1Zh4POr4d1" # admin:smartpay
EOF

# Crear archivo acme.json con permisos correctos
touch /home/smartpayvps/traefik/data/acme.json
chmod 600 /home/smartpayvps/traefik/data/acme.json

# docker-compose.yml para Traefik con puertos alternativos
cat > /home/smartpayvps/traefik/docker-compose.yml << 'EOF'
version: '3'

services:
  traefik:
    image: traefik:v2.10
    container_name: traefik
    restart: unless-stopped
    security_opt:
      - no-new-privileges:true
    ports:
      - "8081:8081"  # HTTP alternativo
      - "8443:8443"  # HTTPS alternativo
      # Dashboard
      - "8080:8080"
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
EOF

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
    echo -e "${GREEN}Dashboard disponible en: https://traefik.smartpay-oficial.com:8080${NC}"
    echo -e "${GREEN}Usuario: admin${NC}"
    echo -e "${GREEN}Contraseña: smartpay${NC}"
    echo ""
    echo -e "${YELLOW}IMPORTANTE: Configuración de puertos${NC}"
    echo "Traefik está configurado para usar los siguientes puertos alternativos:"
    echo "- HTTP: 8081 (en lugar de 80)"
    echo "- HTTPS: 8443 (en lugar de 443)"
    echo ""
    echo -e "${YELLOW}NOTA IMPORTANTE:${NC}"
    echo "Para que los deployments de tiendas funcionen correctamente con estos puertos alternativos,"
    echo "deberá actualizar el servicio de deployment para usar estos puertos."
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
echo -e "${YELLOW}PRÓXIMOS PASOS:${NC}"
echo "1. Actualizar el servicio de deployment para usar los puertos 8081 y 8443"
echo "2. Los nuevos deployments de tiendas ya utilizarán Traefik automáticamente"
echo "3. Para tiendas existentes, necesitará redeployarlas para usar Traefik"
echo ""
