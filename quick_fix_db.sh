#!/bin/bash

echo "=== SOLUCIÓN RÁPIDA PARA VOLUMEN DE BD ==="

# 1. Detener servicios
echo "1. Deteniendo servicios..."
docker-compose -f docker/Docker-compose.vps.yml down

# 2. Crear el volumen postgres_data si no existe
echo "2. Creando volumen postgres_data..."
docker volume create postgres_data

# 3. Migrar datos del volumen anterior si existe
echo "3. Verificando si hay datos para migrar..."
if docker volume ls | grep -q "docker_postgres_data"; then
    echo "   Migrando datos de docker_postgres_data a postgres_data..."
    docker run --rm \
        -v docker_postgres_data:/source \
        -v postgres_data:/dest \
        alpine sh -c "cp -r /source/* /dest/ 2>/dev/null || echo 'Volumen fuente vacío'"
fi

# 4. Iniciar servicios
echo "4. Iniciando servicios..."
docker-compose -f docker/Docker-compose.vps.yml up -d

# 5. Esperar y verificar
echo "5. Esperando a que PostgreSQL esté listo..."
sleep 10

echo "6. Verificación final:"
docker ps --filter "name=smartpay-db" --format "{{.Names}}: {{.Status}}"
docker exec docker-smartpay-db-1 pg_isready -U postgres && echo "✓ PostgreSQL conectado" || echo "✗ Error de conexión"

echo "=== SOLUCIÓN COMPLETADA ==="
