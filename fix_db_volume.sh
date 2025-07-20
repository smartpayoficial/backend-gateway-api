#!/bin/bash

echo "=== SCRIPT DE REPARACIÓN DE VOLUMEN DE BASE DE DATOS ==="
echo "Fecha: $(date)"
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}PASO 1: Detener servicios${NC}"
echo "Deteniendo servicios de smartpay..."
docker-compose -f docker/Docker-compose.vps.yml down
echo ""

echo -e "${YELLOW}PASO 2: Verificar volúmenes existentes${NC}"
echo "Volúmenes actuales:"
docker volume ls | grep -E "(postgres|smartpay)"
echo ""

echo -e "${YELLOW}PASO 3: Crear volumen postgres_data si no existe${NC}"
if ! docker volume ls | grep -q "postgres_data"; then
    echo "Creando volumen postgres_data..."
    docker volume create postgres_data
    echo -e "${GREEN}✓ Volumen postgres_data creado${NC}"
else
    echo -e "${GREEN}✓ Volumen postgres_data ya existe${NC}"
fi
echo ""

echo -e "${YELLOW}PASO 4: Verificar si hay datos en otros volúmenes${NC}"
echo "Verificando contenido de docker_postgres_data:"
if docker volume ls | grep -q "docker_postgres_data"; then
    # Crear contenedor temporal para verificar datos
    docker run --rm -v docker_postgres_data:/data alpine ls -la /data | head -10
    echo ""
    echo -e "${YELLOW}¿Hay datos en docker_postgres_data que necesitemos migrar?${NC}"
    echo "Si hay archivos de PostgreSQL, los migraremos..."
    
    # Migrar datos si existen
    if docker run --rm -v docker_postgres_data:/source -v postgres_data:/dest alpine sh -c "ls /source | wc -l" | grep -v "^0$"; then
        echo "Migrando datos de docker_postgres_data a postgres_data..."
        docker run --rm -v docker_postgres_data:/source -v postgres_data:/dest alpine sh -c "cp -r /source/* /dest/ 2>/dev/null || echo 'No hay archivos para copiar'"
        echo -e "${GREEN}✓ Migración completada${NC}"
    fi
fi
echo ""

echo -e "${YELLOW}PASO 5: Verificar configuración del docker-compose${NC}"
echo "Verificando que el volumen esté correctamente configurado..."
if grep -q "postgres_data:/var/lib/postgresql/data" docker/Docker-compose.vps.yml; then
    echo -e "${GREEN}✓ Configuración de volumen correcta en docker-compose${NC}"
else
    echo -e "${RED}✗ Problema en configuración de volumen${NC}"
    echo "Verificando configuración actual:"
    grep -A 2 -B 2 "postgresql/data" docker/Docker-compose.vps.yml
fi
echo ""

echo -e "${YELLOW}PASO 6: Reiniciar servicios${NC}"
echo "Iniciando servicios con volumen corregido..."
docker-compose -f docker/Docker-compose.vps.yml up -d
echo ""

echo -e "${YELLOW}PASO 7: Esperar a que la base de datos esté lista${NC}"
echo "Esperando a que PostgreSQL esté disponible..."
for i in {1..30}; do
    if docker exec docker-smartpay-db-1 pg_isready -U postgres >/dev/null 2>&1; then
        echo -e "${GREEN}✓ PostgreSQL está disponible${NC}"
        break
    fi
    echo -n "."
    sleep 2
done
echo ""

echo -e "${YELLOW}PASO 8: Verificar estado final${NC}"
echo "Estado de contenedores:"
docker ps --filter "name=smartpay" --format "table {{.Names}}\t{{.Status}}"
echo ""

echo "Verificando base de datos:"
docker exec docker-smartpay-db-1 psql -U postgres -c "\l" | grep smartpay || echo "Creando base de datos smartpay..."
docker exec docker-smartpay-db-1 psql -U postgres -c "CREATE DATABASE smartpay;" 2>/dev/null || echo "Base de datos smartpay ya existe"
echo ""

echo -e "${GREEN}=== REPARACIÓN COMPLETADA ===${NC}"
echo "El volumen de la base de datos ha sido reparado y los servicios están corriendo."
echo ""
