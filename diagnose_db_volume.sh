#!/bin/bash

echo "=== DIAGNÓSTICO DE VOLUMEN DE BASE DE DATOS ==="
echo "Fecha: $(date)"
echo ""

echo "1. Estado de contenedores relacionados con smartpay:"
docker ps -a --filter "name=smartpay" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "2. Volúmenes de Docker existentes:"
docker volume ls | grep -E "(postgres|smartpay)" || echo "No se encontraron volúmenes relacionados"
echo ""

echo "3. Información detallada del volumen postgres_data:"
docker volume inspect postgres_data 2>/dev/null || echo "El volumen postgres_data no existe"
echo ""

echo "4. Verificar si el contenedor de DB está corriendo:"
DB_CONTAINER=$(docker ps --filter "name=smartpay-db" --format "{{.Names}}")
if [ -n "$DB_CONTAINER" ]; then
    echo "Contenedor de DB encontrado: $DB_CONTAINER"
    echo "Logs recientes del contenedor de DB:"
    docker logs --tail 20 $DB_CONTAINER
    echo ""
    echo "Verificar conexión a la base de datos:"
    docker exec $DB_CONTAINER pg_isready -U postgres || echo "No se puede conectar a PostgreSQL"
    echo ""
    echo "Listar bases de datos:"
    docker exec $DB_CONTAINER psql -U postgres -c "\l" || echo "Error al listar bases de datos"
else
    echo "No se encontró contenedor de DB corriendo"
fi
echo ""

echo "5. Verificar archivos en el directorio de datos del contenedor:"
if [ -n "$DB_CONTAINER" ]; then
    echo "Contenido del directorio /var/lib/postgresql/data:"
    docker exec $DB_CONTAINER ls -la /var/lib/postgresql/data/ || echo "Error al acceder al directorio de datos"
else
    echo "No se puede verificar - contenedor no está corriendo"
fi
echo ""

echo "6. Información del sistema de archivos del host:"
echo "Espacio en disco disponible:"
df -h
echo ""

echo "7. Verificar procesos de PostgreSQL:"
docker exec $DB_CONTAINER ps aux | grep postgres 2>/dev/null || echo "No se pueden verificar procesos - contenedor no accesible"
echo ""

echo "=== FIN DEL DIAGNÓSTICO ==="
