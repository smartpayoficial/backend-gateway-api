#!/bin/bash

echo "=== DIAGNÓSTICO CORREGIDO DE VOLUMEN DE BASE DE DATOS ==="
echo "Fecha: $(date)"
echo ""

echo "1. Estado de contenedores relacionados con smartpay:"
docker ps -a --filter "name=smartpay" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "2. Volúmenes de Docker existentes:"
docker volume ls
echo ""

echo "3. Información detallada de volúmenes relevantes:"
echo "--- docker_postgres_data ---"
docker volume inspect docker_postgres_data 2>/dev/null || echo "El volumen docker_postgres_data no existe"
echo ""
echo "--- smartpay-db ---"
docker volume inspect smartpay-db 2>/dev/null || echo "El volumen smartpay-db no existe"
echo ""

echo "4. Verificar contenedor de base de datos específico:"
DB_CONTAINER="docker-smartpay-db-1"
echo "Verificando contenedor: $DB_CONTAINER"
if docker ps --filter "name=$DB_CONTAINER" --format "{{.Names}}" | grep -q "$DB_CONTAINER"; then
    echo "✓ Contenedor está corriendo"
    echo ""
    echo "Logs recientes del contenedor:"
    docker logs --tail 10 $DB_CONTAINER
    echo ""
    echo "Verificar conexión PostgreSQL:"
    docker exec $DB_CONTAINER pg_isready -U postgres || echo "✗ No se puede conectar a PostgreSQL"
    echo ""
    echo "Contenido del directorio de datos:"
    docker exec $DB_CONTAINER ls -la /var/lib/postgresql/data/ || echo "✗ Error al acceder al directorio de datos"
    echo ""
    echo "Verificar si la base de datos smartpay existe:"
    docker exec $DB_CONTAINER psql -U postgres -c "\l" | grep smartpay || echo "✗ Base de datos smartpay no encontrada"
else
    echo "✗ Contenedor no está corriendo"
fi
echo ""

echo "5. Verificar configuración del docker-compose:"
echo "Revisando volúmenes definidos en docker-compose:"
if [ -f "docker/Docker-compose.vps.yml" ]; then
    echo "Volúmenes definidos:"
    grep -A 10 "volumes:" docker/Docker-compose.vps.yml | tail -5
else
    echo "✗ Archivo docker-compose no encontrado"
fi
echo ""

echo "6. Verificar montajes de volúmenes en el contenedor:"
docker inspect $DB_CONTAINER --format='{{range .Mounts}}{{.Source}} -> {{.Destination}} ({{.Type}}){{"\n"}}{{end}}' 2>/dev/null || echo "✗ No se puede inspeccionar el contenedor"
echo ""

echo "=== FIN DEL DIAGNÓSTICO CORREGIDO ==="
