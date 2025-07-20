"""
Configuración centralizada para el sistema de deployment automático.
Este archivo contiene todas las configuraciones importantes del sistema.
"""

import os
from pathlib import Path

# Configuración de rutas base
BASE_BACKEND_PATH = "/home/danielamg/Escritorio/trabajo/olimpo/smart-pay/backend-gateway-api"
BASE_DB_PATH = "/home/danielamg/Escritorio/trabajo/olimpo/smart-pay/db-smartpay"
DEPLOYMENT_BASE_PATH = "/home/danielamg/Escritorio/trabajo/olimpo/smart-pay/deployments"

# Configuración de puertos
PORT_RANGE_START = 9000
PORT_RANGE_END = 9999
MAX_DEPLOYMENTS = PORT_RANGE_END - PORT_RANGE_START

# Configuración de Docker
DOCKER_COMPOSE_TIMEOUT = 300  # 5 minutos
DOCKER_STOP_TIMEOUT = 120     # 2 minutos

# Configuración de red
DOCKER_NETWORK_PREFIX = "smartpay"

# Configuración de logging
LOG_LEVEL = "INFO"

# Plantilla de docker-compose
DOCKER_COMPOSE_TEMPLATE = """services:
  api-{store_id}:
    build:
      context: .
      dockerfile: docker/Dockerfile
    container_name: backend-api-{store_id}
    ports:
      - "{backend_port}:8000"
      - "{websocket_port}:8001"
    environment:
      HOST: 0.0.0.0
      PORT: 8000
      PYTHONUNBUFFERED: 1
      PYTHONPATH: /app
      SOCKETIO_ASYNC_MODE: asgi
      DB_API: http://smartpay-db-api-{store_id}:{db_port}
      USER_SVC_URL: http://smartpay-db-api-{store_id}:{db_port}
      REDIRECT_URI: https://smartpay-oficial.com:{backend_port}/api/v1/google/auth/callback
      CLIENT_SECRET: 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
      CLIENT_ID: 631597337466-dt7qitq7tg2022rhje5ib5sk0eua6t79.apps.googleusercontent.com
      SMTP_SERVER: smtp.gmail.com
      SMTP_PORT: 587
      SMTP_USERNAME: smartpay.noreply@gmail.com
      SMTP_PASSWORD: 'jgiz oqck snoj icwz'
      EMAIL_FROM: smartpay.noreply@gmail.com
      RESET_PASSWORD_BASE_URL: https://smartpay-oficial.com/reset-password
    volumes:
      - .:/app
      - ./logs:/app/logs
      - /etc/ssl/smartpay:/etc/ssl/smartpay:ro
    restart: unless-stopped
    extra_hosts:
      - "host.docker.internal:host-gateway"
    sysctls:
      - net.core.somaxconn=65535
    ulimits:
      nofile:
        soft: 65535
        hard: 65535
    networks:
      - {network_name}

networks:
  {network_name}:
    driver: bridge
"""

def validate_configuration():
    """Valida que la configuración sea correcta."""
    errors = []
    
    # Verificar que las rutas base existen
    if not os.path.exists(BASE_BACKEND_PATH):
        errors.append(f"Ruta base del backend no existe: {BASE_BACKEND_PATH}")
    
    if not os.path.exists(BASE_DB_PATH):
        errors.append(f"Ruta base de la DB no existe: {BASE_DB_PATH} (opcional)")
    
    # Verificar que el directorio de deployments se puede crear
    try:
        Path(DEPLOYMENT_BASE_PATH).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        errors.append(f"No se puede crear directorio de deployments: {e}")
    
    # Verificar configuración de puertos
    if PORT_RANGE_START >= PORT_RANGE_END:
        errors.append("PORT_RANGE_START debe ser menor que PORT_RANGE_END")
    
    if PORT_RANGE_START < 1024:
        errors.append("PORT_RANGE_START debe ser mayor que 1024 (puertos privilegiados)")
    
    return errors

def get_deployment_paths(store_id):
    """Obtiene las rutas de deployment para una tienda."""
    return {
        "backend_path": f"{DEPLOYMENT_BASE_PATH}/backend-gateway-api-{store_id}",
        "db_path": f"{DEPLOYMENT_BASE_PATH}/db-smartpay-{store_id}"
    }

def get_network_name(store_id):
    """Obtiene el nombre de la red Docker para una tienda."""
    return f"{DOCKER_NETWORK_PREFIX}-{store_id}"

def generate_docker_compose(store_id, ports):
    """Genera el contenido del docker-compose para una tienda."""
    return DOCKER_COMPOSE_TEMPLATE.format(
        store_id=store_id,
        backend_port=ports["backend_port"],
        websocket_port=ports["websocket_port"],
        db_port=ports["db_port"],
        network_name=get_network_name(store_id)
    )

if __name__ == "__main__":
    """Ejecutar validación de configuración."""
    print("🔧 Validando configuración del sistema de deployment...")
    
    errors = validate_configuration()
    
    if errors:
        print("❌ Errores de configuración encontrados:")
        for error in errors:
            print(f"   - {error}")
    else:
        print("✅ Configuración válida")
        print(f"   - Ruta base backend: {BASE_BACKEND_PATH}")
        print(f"   - Ruta base DB: {BASE_DB_PATH}")
        print(f"   - Directorio deployments: {DEPLOYMENT_BASE_PATH}")
        print(f"   - Rango de puertos: {PORT_RANGE_START}-{PORT_RANGE_END}")
        print(f"   - Máximo deployments: {MAX_DEPLOYMENTS}")
