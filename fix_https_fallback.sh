#!/bin/bash

echo "=== SOLUCIÓN DE RESPALDO: HTTPS EN PUERTO 8443 ==="
echo "Fecha: $(date)"
echo ""

echo "1. Deteniendo servicios..."
docker-compose -f docker/Docker-compose.vps.yml down
echo ""

echo "2. Creando configuración temporal con puerto 8443..."

# Backup del docker-compose original
cp docker/Docker-compose.vps.yml docker/Docker-compose.vps.yml.backup

# Crear versión temporal con puerto 8443
cat > docker/Docker-compose.vps.yml.temp << 'EOF'
version: '3.8'
services:
  api:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    container_name: backend-api
    ports:
      - "8443:8443"   # Puerto HTTPS no privilegiado
      - "8001:8001"   # Puerto para WebSocket
    environment:
      HOST: 0.0.0.0
      PORT: 8443
      PYTHONUNBUFFERED: 1
      PYTHONPATH: /app
      SOCKETIO_ASYNC_MODE: asgi
      SOCKETIO_CORS_ALLOWED_ORIGINS: "*"
      USER_SVC_URL: http://smartpay-db-api:8002
      REDIRECT_URI: https://smartpay-oficial.com:8443/api/v1/google/auth/callback
      CLIENT_SECRET: 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
      CLIENT_ID: 631597337466-dt7qitq7tg2022rhje5ib5sk0eua6t79.apps.googleusercontent.com
      # Configuración de correo electrónico
      SMTP_SERVER: smtp.gmail.com
      SMTP_PORT: 587
      SMTP_USERNAME: smartpayoficial@gmail.com
      SMTP_PASSWORD: nfqj kqjb vhcw ypzd
      FROM_EMAIL: smartpayoficial@gmail.com
      RESET_PASSWORD_BASE_URL: https://smartpay-oficial.com:8443/reset-password
    volumes:
      - /etc/ssl/smartpay:/etc/ssl/smartpay:ro
      - /var/run/docker.sock:/var/run/docker.sock
      - /home/smartpayvps:/host/smartpayvps
    networks:
      - smartpay-network
    depends_on:
      - smartpay-db-v12
    restart: unless-stopped
    extra_hosts:
      - "host.docker.internal:host-gateway"
    # Comando SSL se toma del Dockerfile (modificado para puerto 8443)
    command: ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8443", "--ssl-certfile=/etc/ssl/smartpay/fullchain.pem", "--ssl-keyfile=/etc/ssl/smartpay/smartpay-oficial.com-PrivateKey.pem"]
    sysctls:
      - net.core.somaxconn=65535
    ulimits:
      nofile:
        soft: 65536
        hard: 65536

  smartpay-db-v12:
    image: postgres:12
    container_name: docker-smartpay-db-v12-1
    environment:
      POSTGRES_DB: smartpay
      POSTGRES_USER: smartpay
      POSTGRES_PASSWORD: smartpay123
    ports:
      - "5433:5432"
    volumes:
      - smartpay-db-prod:/var/lib/postgresql/data
    networks:
      - smartpay-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U smartpay -d smartpay"]
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  smartpay-network:
    driver: bridge

volumes:
  smartpay-db-prod:
    driver: local
    name: smartpay-db-prod
EOF

echo "3. Usando configuración temporal..."
mv docker/Docker-compose.vps.yml.temp docker/Docker-compose.vps.yml

echo "4. Reconstruyendo con puerto 8443..."
docker-compose -f docker/Docker-compose.vps.yml build --no-cache

echo "5. Iniciando servicios en puerto 8443..."
docker-compose -f docker/Docker-compose.vps.yml up -d

echo "6. Esperando inicio..."
sleep 25

echo "7. Verificando servicios..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "8. Probando conectividad..."
echo "   HTTPS puerto 8443:"
curl -k -s -o /dev/null -w "Status: %{http_code}\n" https://localhost:8443/ || echo "   ❌ Falló"
echo "   HTTPS dominio con puerto:"
curl -k -s -o /dev/null -w "Status: %{http_code}\n" https://smartpay-oficial.com:8443/ || echo "   ❌ Falló"
echo ""

echo "9. Logs del servicio..."
docker logs backend-api --tail 10
echo ""

echo "=== SOLUCIÓN DE RESPALDO APLICADA ==="
echo "Si funciona, el servicio estará disponible en:"
echo "  - https://smartpay-oficial.com:8443"
echo "  - https://localhost:8443"
echo ""
echo "Para volver a la configuración original:"
echo "  mv docker/Docker-compose.vps.yml.backup docker/Docker-compose.vps.yml"
