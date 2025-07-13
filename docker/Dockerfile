FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=8000 \
    PYTHONPATH=/app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    curl \
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

# Puerto de la aplicación
EXPOSE 8000

#RUN mkdir -p /etc/ssl/smartpay

COPY . /app

# Comando para iniciar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--ssl-certfile=/etc/ssl/smartpay/fullchain.pem", "--ssl-keyfile=/etc/ssl/smartpay/smartpay-oficial.com-PrivateKey.pem"]
#CMD ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"]