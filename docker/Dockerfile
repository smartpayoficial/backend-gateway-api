FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=8000 \
    PYTHONPATH=/app

# Instalar dependencias del sistema incluyendo Docker
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    curl \
    ca-certificates \
    gnupg \
    lsb-release \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update \
    && apt-get install -y --no-install-recommends docker-ce-cli docker-compose-plugin \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Instalar dependencias de prueba
COPY test-requirements.txt .
RUN pip install --no-cache-dir -r test-requirements.txt

# Copiar la aplicación
# COPY . .  <-- This is commented out to rely on the volume mount in docker-compose.dev.yml

# Crear endpoint de health check
RUN echo 'from fastapi import FastAPI; app = FastAPI(); @app.get("/health") \
def health_check(): return {"status": "healthy"}' > /app/health_check.py

# Puerto de la aplicación (HTTPS)
EXPOSE 443
EXPOSE 8001

#RUN mkdir -p /etc/ssl/smartpay

COPY . /app

# Comando para iniciar la aplicación con SSL
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "443", "--ssl-certfile=/etc/ssl/smartpay/fullchain.pem", "--ssl-keyfile=/etc/ssl/smartpay/smartpay-oficial.com-PrivateKey.pem"]