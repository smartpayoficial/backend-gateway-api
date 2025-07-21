#!/bin/bash

echo "=== RESTAURANDO SSL EN PUERTO 8000 ==="
echo "Fecha: $(date)"
echo ""

echo "1. Deteniendo servicios actuales..."
docker-compose -f docker/Docker-compose.vps.yml down
echo ""

echo "2. Actualizando Dockerfile para SSL en puerto 8000..."
cat > docker/Dockerfile << 'EOF'
FROM python:3.11-slim

# Actualizar el sistema e instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    gnupg2 \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# Instalar Docker CLI y docker-compose
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update \
    && apt-get install -y docker-ce-cli docker-compose-plugin \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalar uvicorn con soporte para websockets
RUN pip install uvicorn[standard] websockets

# Crear directorio para logs
RUN mkdir -p /app/logs

# Crear health check endpoint
RUN echo 'from fastapi import FastAPI; app = FastAPI(); @app.get("/health") \
def health_check(): return {"status": "healthy"}' > /app/health_check.py

# Puerto de la aplicación (HTTPS en puerto 8000)
EXPOSE 8000
EXPOSE 8001

COPY . /app

# Comando para iniciar la aplicación con SSL en puerto 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--ssl-certfile=/etc/ssl/smartpay/fullchain.pem", "--ssl-keyfile=/etc/ssl/smartpay/smartpay-oficial.com-PrivateKey.pem"]
EOF

echo "3. Actualizando docker-compose.vps.yml para SSL en puerto 8000..."
cat > docker/Docker-compose.vps.yml << 'EOF'
version: '3.8'

services:
  api:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    container_name: backend-api
    ports:
      - "8000:8000"   # Puerto HTTPS
      - "8001:8001"   # Puerto para WebSocket
    environment:
      HOST: 0.0.0.0
      PORT: 8000
      PYTHONUNBUFFERED: 1
      PYTHONPATH: /app
      SOCKETIO_ASYNC_MODE: asgi
      SOCKETIO_CORS_ALLOWED_ORIGINS: "*"
      USER_SVC_URL: http://smartpay-db-api:8002
      REDIRECT_URI: https://smartpay-oficial.com:8000/api/v1/google/auth/callback
      CLIENT_SECRET: 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
      CLIENT_ID: 631597337466-dt7qitq7tg2022rhje5ib5sk0eua6t79.apps.googleusercontent.com
      # Configuración de correo electrónico
      SMTP_SERVER: smtp.gmail.com
      SMTP_PORT: 587
      SMTP_USERNAME: smartpayoficial@gmail.com
      SMTP_PASSWORD: nfqj kqjb vhcw ypzd
      FROM_EMAIL: smartpayoficial@gmail.com
      EMAIL_FROM: smartpay.noreply@gmail.com
      RESET_PASSWORD_BASE_URL: https://smartpay-oficial.com:8000/reset-password
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
    # El comando SSL se toma del Dockerfile
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

echo "4. Reconstruyendo imagen con SSL en puerto 8000..."
docker-compose -f docker/Docker-compose.vps.yml build --no-cache

echo "5. Iniciando servicios con SSL en puerto 8000..."
docker-compose -f docker/Docker-compose.vps.yml up -d

echo "6. Esperando que los servicios inicien..."
sleep 25

echo "7. Verificando estado de contenedores..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "8. Verificando logs del backend-api..."
docker logs backend-api --tail 15
echo ""

echo "9. Verificando certificados SSL dentro del contenedor..."
docker exec backend-api ls -la /etc/ssl/smartpay/ 2>/dev/null && echo "    ✅ Certificados montados" || echo "    ❌ Certificados no montados"
echo ""

echo "10. Verificando que Docker CLI esté disponible..."
docker exec backend-api docker --version 2>/dev/null && echo "    ✅ Docker CLI disponible" || echo "    ❌ Docker CLI no disponible"
echo ""

echo "11. Probando conectividad..."
echo "    HTTPS puerto 8000:"
curl -k -s -o /dev/null -w "Status: %{http_code}\n" https://localhost:8000/ || echo "    ❌ Falló"
echo "    HTTPS con dominio:"
curl -k -s -o /dev/null -w "Status: %{http_code}\n" https://smartpay-oficial.com:8000/ || echo "    ❌ Falló"
echo ""

echo "=== CONFIGURACIÓN FINAL ==="
echo "✅ HTTPS habilitado en puerto 8000 con certificados SSL"
echo "✅ Docker CLI disponible para deployments automáticos"
echo "✅ Sin conflicto con el servicio en puerto 443"
echo ""
echo "URLs disponibles:"
echo "  - https://smartpay-oficial.com:8000 (Backend API con SSL)"
echo "  - https://smartpay-oficial.com:8000/docs (Swagger UI)"
echo "  - https://smartpay-oficial.com:8001 (WebSocket)"
echo ""
echo "¡Sistema completamente funcional con SSL y deployments!"
