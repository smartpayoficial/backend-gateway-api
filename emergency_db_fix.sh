#!/bin/bash

echo "🚑 REPARACIÓN DE EMERGENCIA - BASE DE DATOS 🚑"
echo "=============================================="

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}PASO 1: Crear base de datos si no existe...${NC}"
docker exec docker-smartpay-db-1 psql -U postgres -c "CREATE DATABASE smartpay;" 2>/dev/null || echo "Base de datos ya existe"

echo ""
echo -e "${YELLOW}PASO 2: Verificar/crear usuario de aplicación...${NC}"
docker exec docker-smartpay-db-1 psql -U postgres -c "
CREATE USER smartpay_user WITH PASSWORD 'smartpay123';
GRANT ALL PRIVILEGES ON DATABASE smartpay TO smartpay_user;
ALTER USER smartpay_user CREATEDB;
" 2>/dev/null || echo "Usuario ya existe o error en creación"

echo ""
echo -e "${YELLOW}PASO 3: Ejecutar migraciones de la aplicación...${NC}"

# Verificar si hay alembic
if [ -f "alembic.ini" ]; then
    echo "Ejecutando migraciones con Alembic..."
    docker exec backend-api alembic upgrade head || echo "Error en migraciones Alembic"
elif [ -f "app/db/migrations.py" ] || [ -d "app/db/migrations" ]; then
    echo "Ejecutando migraciones personalizadas..."
    docker exec backend-api python -m app.db.migrations || echo "Error en migraciones personalizadas"
else
    echo "No se encontraron archivos de migración, creando estructura básica..."
    
    # Crear estructura básica de tablas comunes
    docker exec docker-smartpay-db-1 psql -U postgres -d smartpay -c "
    -- Tabla de usuarios
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        name VARCHAR(255) NOT NULL,
        password_hash VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Tabla de tiendas
    CREATE TABLE IF NOT EXISTS stores (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        country_id INTEGER,
        plan VARCHAR(100),
        tokens_disponibles INTEGER DEFAULT 0,
        back_link VARCHAR(500),
        db_link VARCHAR(500),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Tabla de países
    CREATE TABLE IF NOT EXISTS countries (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        code VARCHAR(10) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Insertar algunos países básicos
    INSERT INTO countries (name, code) VALUES 
        ('Colombia', 'CO'),
        ('México', 'MX'),
        ('Argentina', 'AR'),
        ('Chile', 'CL'),
        ('Perú', 'PE')
    ON CONFLICT DO NOTHING;
    
    -- Crear índices
    CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
    CREATE INDEX IF NOT EXISTS idx_stores_name ON stores(name);
    
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO smartpay_user;
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO smartpay_user;
    "
fi

echo ""
echo -e "${YELLOW}PASO 4: Verificar estructura creada...${NC}"
echo "Tablas creadas:"
docker exec docker-smartpay-db-1 psql -U postgres -d smartpay -c "\dt"

echo ""
echo "Conteo de registros:"
docker exec docker-smartpay-db-1 psql -U postgres -d smartpay -c "
SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.tables WHERE table_name = t.table_name AND table_schema = 'public') as exists,
    CASE 
        WHEN table_name = 'users' THEN (SELECT COUNT(*) FROM users)
        WHEN table_name = 'stores' THEN (SELECT COUNT(*) FROM stores)
        WHEN table_name = 'countries' THEN (SELECT COUNT(*) FROM countries)
        ELSE 0
    END as row_count
FROM (VALUES ('users'), ('stores'), ('countries')) as t(table_name);
" 2>/dev/null || echo "Error al contar registros"

echo ""
echo -e "${YELLOW}PASO 5: Reiniciar servicios para aplicar cambios...${NC}"
docker restart backend-api smartpay-db-api

echo ""
echo -e "${YELLOW}PASO 6: Verificación final...${NC}"
sleep 5
echo "Estado de servicios:"
docker ps --filter "name=smartpay" --format "table {{.Names}}\t{{.Status}}"

echo ""
echo "Prueba de conectividad de la API:"
curl -X GET http://localhost:8002/health 2>/dev/null | head -1 || echo "API no responde aún"

echo ""
echo -e "${GREEN}🚑 REPARACIÓN DE EMERGENCIA COMPLETADA 🚑${NC}"
echo "La base de datos debería tener ahora estructura básica y estar funcionando."
