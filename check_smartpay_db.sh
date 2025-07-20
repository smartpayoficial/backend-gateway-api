#!/bin/bash

echo "🔍 VERIFICANDO VOLUMEN smartpay-db 🔍"
echo "==================================="

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}1. EXPLORANDO VOLUMEN smartpay-db...${NC}"
echo "Contenido del volumen smartpay-db:"
docker run --rm -v smartpay-db:/data alpine sh -c "
echo 'Archivos en el directorio raíz:';
ls -la /data/;
echo '';
echo 'Verificando si es PostgreSQL:';
if [ -f /data/PG_VERSION ]; then
    echo 'SÍ ES POSTGRESQL - Versión:';
    cat /data/PG_VERSION;
    echo '';
    echo 'Archivos de configuración:';
    ls -la /data/*.conf;
    echo '';
    echo 'Bases de datos (directorios en base/):';
    ls -la /data/base/ | head -10;
    echo '';
    echo 'Tamaño del volumen:';
    du -sh /data/;
else
    echo 'NO es PostgreSQL, verificando otros tipos de datos:';
    find /data -type f -name '*.sql' -o -name '*.db' -o -name '*.json' | head -10;
fi
"

echo ""
echo -e "${YELLOW}2. COMPARANDO CON docker_postgres_data...${NC}"
echo "Contenido de docker_postgres_data:"
docker run --rm -v docker_postgres_data:/data alpine sh -c "
echo 'Tamaño:';
du -sh /data/;
echo 'Última modificación:';
ls -lat /data/ | head -5;
"

echo ""
echo "Contenido de smartpay-db:"
docker run --rm -v smartpay-db:/data alpine sh -c "
echo 'Tamaño:';
du -sh /data/;
echo 'Última modificación:';
ls -lat /data/ | head -5;
"

echo ""
echo -e "${YELLOW}3. PROBANDO RECUPERACIÓN CON smartpay-db...${NC}"
read -p "¿Quieres probar recuperar desde smartpay-db? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Deteniendo servicios..."
    docker-compose -f docker/Docker-compose.vps.yml down
    
    echo "Respaldando volumen actual..."
    docker volume create postgres_data_backup_2 2>/dev/null || echo "Backup ya existe"
    docker run --rm \
        -v postgres_data:/source \
        -v postgres_data_backup_2:/backup \
        alpine sh -c "cp -a /source/. /backup/ 2>/dev/null || echo 'Volumen fuente vacío'"
    
    echo "Reemplazando con smartpay-db..."
    docker volume rm postgres_data 2>/dev/null || echo "Volumen no existía"
    docker volume create postgres_data
    
    docker run --rm \
        -v smartpay-db:/source \
        -v postgres_data:/dest \
        alpine sh -c "
        echo 'Copiando datos...';
        cp -a /source/. /dest/;
        echo 'Verificando:';
        ls -la /dest/ | head -5;
        "
    
    echo "Iniciando servicios..."
    docker-compose -f docker/Docker-compose.vps.yml up -d
    
    echo "Esperando PostgreSQL..."
    sleep 15
    
    echo "Verificando recuperación:"
    docker exec docker-smartpay-db-1 pg_isready -U postgres
    docker exec docker-smartpay-db-1 psql -U postgres -c "\l"
    
    echo "Verificando datos en smartpay:"
    docker exec docker-smartpay-db-1 psql -U postgres -d smartpay -c "\dt" 2>/dev/null || echo "Base smartpay no existe"
    
    echo "Probando endpoints:"
    sleep 5
    curl -s -X GET "http://localhost:8002/api/v1/countries/" | jq '. | length' 2>/dev/null || curl -s -X GET "http://localhost:8002/api/v1/countries/"
    
else
    echo "Recuperación cancelada"
fi

echo ""
echo -e "${YELLOW}4. ALTERNATIVA: BUSCAR BACKUPS EN EL SISTEMA...${NC}"
echo "Buscando archivos de backup SQL:"
find /home -name "*.sql" -o -name "*backup*" -o -name "*dump*" 2>/dev/null | grep -i smartpay | head -10

echo ""
echo "Buscando en directorio de usuario:"
find ~/. -name "*smartpay*" -o -name "*backup*" 2>/dev/null | head -10

echo ""
echo "Verificando si hay backups automáticos de Docker:"
find /var/lib/docker/volumes -name "*smartpay*" 2>/dev/null | head -10

echo ""
echo -e "${YELLOW}5. OPCIÓN NUCLEAR: CREAR DATOS DESDE CERO...${NC}"
echo "Si no encontramos los datos originales, podemos:"
echo "1. Crear estructura completa desde cero"
echo "2. Poblar con datos de ejemplo"
echo "3. Configurar para que funcione inmediatamente"

echo ""
echo -e "${GREEN}🔍 VERIFICACIÓN COMPLETADA 🔍${NC}"
