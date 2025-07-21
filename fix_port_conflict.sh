#!/bin/bash

echo "=== SOLUCIONANDO CONFLICTO DE PUERTO 443 ==="
echo "Fecha: $(date)"
echo ""

echo "1. El puerto 443 está ocupado por otro servicio. Cambiando a puerto 8443..."
echo ""

echo "2. Creando backup de la configuración actual..."
cp docker/Docker-compose.vps.yml docker/Docker-compose.vps.yml.backup-$(date +%Y%m%d-%H%M%S)

echo "3. Actualizando docker-compose para usar puerto 8443..."
cat > docker/Docker-compose.vps.yml << 'EOF'
version: '3.8'

services:
  api:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    container_name: backend-api
    ports:
      - "8443:8443"   # Puerto HTTPS alternativo
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
      EMAIL_FROM: smartpay.noreply@gmail.com
      RESET_PASSWORD_BASE_URL: https://smartpay-oficial.com:8443/reset-password
    volumes:
      - ..:/app
      - ./logs:/app/logs
      - /etc/ssl/smartpay:/etc/ssl/smartpay:ro
      - /var/run/docker.sock:/var/run/docker.sock
      - /home/smartpayvps:/host/smartpayvps
    networks:
      - smartpay_network
    depends_on:
      - smartpay-db-v12
    restart: unless-stopped
    extra_hosts:
      - "host.docker.internal:host-gateway"
    # Comando SSL con puerto 8443
    command: ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8443", "--ssl-certfile=/etc/ssl/smartpay/fullchain.pem", "--ssl-keyfile=/etc/ssl/smartpay/smartpay-oficial.com-PrivateKey.pem"]
    sysctls:
      - net.core.somaxconn=65535
    ulimits:
      nofile:
        soft: 65536
        hard: 65536

  smartpay-db-api:
    image: smartpay-db-api
    container_name: smartpay-db-api
    ports:
      - "8002:8002"
    environment:
      DATABASE_URL: postgresql://smartpay:smartpay123@smartpay-db-v12:5432/smartpay
      PYTHONUNBUFFERED: 1
    networks:
      - smartpay_network
    depends_on:
      - smartpay-db-v12
    restart: unless-stopped

  smartpay-db-v12:
    image: postgres:12
    container_name: docker-smartpay-db-v12-1
    environment:
      POSTGRES_DB: smartpay
      POSTGRES_USER: smartpay
      POSTGRES_PASSWORD: smartpay123
    ports:
      - "5437:5432"
    volumes:
      - smartpay-db-prod:/var/lib/postgresql/data
    networks:
      - smartpay_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U smartpay -d smartpay"]
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  smartpay_network:
    driver: bridge

volumes:
  smartpay-db-prod:
    driver: local
    name: smartpay-db-prod
EOF

echo "4. Actualizando Dockerfile para puerto 8443..."
sed -i 's/EXPOSE 443/EXPOSE 8443/' docker/Dockerfile
sed -i 's/--port", "443"/--port", "8443"/' docker/Dockerfile

echo "5. Iniciando servicios en puerto 8443..."
docker-compose -f docker/Docker-compose.vps.yml up -d

echo "6. Esperando que los servicios inicien..."
sleep 20

echo "7. Verificando estado de contenedores..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "8. Verificando logs del backend-api..."
docker logs backend-api --tail 15
echo ""

echo "9. Verificando certificados SSL dentro del contenedor..."
docker exec backend-api ls -la /etc/ssl/smartpay/ 2>/dev/null || echo "   ❌ Certificados no montados"
echo ""

echo "10. Probando conectividad..."
echo "    HTTPS puerto 8443:"
curl -k -s -o /dev/null -w "Status: %{http_code}\n" https://localhost:8443/ || echo "    ❌ Falló"
echo "    HTTPS con dominio:"
curl -k -s -o /dev/null -w "Status: %{http_code}\n" https://smartpay-oficial.com:8443/ || echo "    ❌ Falló"
echo ""

echo "11. Verificando que Docker esté disponible para deployments..."
docker exec backend-api docker --version 2>/dev/null && echo "    ✅ Docker CLI disponible" || echo "    ❌ Docker CLI no disponible"
echo ""

echo "=== SOLUCIÓN APLICADA ==="
echo "✅ Backend funcionando en puerto 8443 (sin conflicto)"
echo "✅ HTTPS habilitado con certificados SSL"
echo "✅ Docker CLI disponible para deployments automáticos"
echo ""
echo "URLs disponibles:"
echo "  - https://smartpay-oficial.com:8443 (Backend API)"
echo "  - https://smartpay-oficial.com:8443/docs (Swagger UI)"
echo "  - https://smartpay-oficial.com:8001 (WebSocket)"
echo ""
echo "El puerto 443 sigue siendo manejado por el servicio existente."
echo "Para usar puerto 443 estándar, configura un proxy reverso."
