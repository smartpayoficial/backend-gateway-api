#!/bin/bash

echo "🚨 POBLACIÓN DE DATOS DE EMERGENCIA 🚨"
echo "====================================="

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}INSERTANDO DATOS DE EMERGENCIA...${NC}"

docker exec docker-smartpay-db-1 psql -U postgres -d smartpay -c "
-- Insertar países
INSERT INTO country (id, name, code, created_at) VALUES 
(1, 'Colombia', 'CO', NOW()),
(2, 'México', 'MX', NOW()),
(3, 'Argentina', 'AR', NOW()),
(4, 'Chile', 'CL', NOW()),
(5, 'Perú', 'PE', NOW()),
(6, 'Brasil', 'BR', NOW()),
(7, 'Ecuador', 'EC', NOW()),
(8, 'Venezuela', 'VE', NOW()),
(9, 'Uruguay', 'UY', NOW()),
(10, 'Paraguay', 'PY', NOW())
ON CONFLICT (id) DO UPDATE SET 
    name = EXCLUDED.name,
    code = EXCLUDED.code;

-- Insertar regiones
INSERT INTO region (id, name, country_id, created_at) VALUES 
(1, 'Bogotá D.C.', 1, NOW()),
(2, 'Antioquia', 1, NOW()),
(3, 'Valle del Cauca', 1, NOW()),
(4, 'Atlántico', 1, NOW()),
(5, 'Cundinamarca', 1, NOW()),
(6, 'Ciudad de México', 2, NOW()),
(7, 'Jalisco', 2, NOW()),
(8, 'Nuevo León', 2, NOW()),
(9, 'Buenos Aires', 3, NOW()),
(10, 'Córdoba', 3, NOW())
ON CONFLICT (id) DO UPDATE SET 
    name = EXCLUDED.name,
    country_id = EXCLUDED.country_id;

-- Insertar ciudades
INSERT INTO city (id, name, region_id, created_at) VALUES 
(1, 'Bogotá', 1, NOW()),
(2, 'Medellín', 2, NOW()),
(3, 'Cali', 3, NOW()),
(4, 'Barranquilla', 4, NOW()),
(5, 'Cartagena', 4, NOW()),
(6, 'Bucaramanga', 5, NOW()),
(7, 'Ciudad de México', 6, NOW()),
(8, 'Guadalajara', 7, NOW()),
(9, 'Monterrey', 8, NOW()),
(10, 'Buenos Aires', 9, NOW())
ON CONFLICT (id) DO UPDATE SET 
    name = EXCLUDED.name,
    region_id = EXCLUDED.region_id;

-- Insertar planes
INSERT INTO plan (id, name, description, price, features, created_at) VALUES 
(1, 'Básico', 'Plan básico para pequeños comercios', 29.99, '{\"max_devices\": 5, \"support\": \"email\"}', NOW()),
(2, 'Profesional', 'Plan profesional para medianos comercios', 59.99, '{\"max_devices\": 15, \"support\": \"phone\"}', NOW()),
(3, 'Empresarial', 'Plan empresarial para grandes comercios', 99.99, '{\"max_devices\": 50, \"support\": \"priority\"}', NOW()),
(4, 'Premium', 'Plan premium con todas las características', 149.99, '{\"max_devices\": -1, \"support\": \"dedicated\"}', NOW())
ON CONFLICT (id) DO UPDATE SET 
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    price = EXCLUDED.price,
    features = EXCLUDED.features;

-- Insertar roles
INSERT INTO role (id, name, description, permissions, created_at) VALUES 
(1, 'admin', 'Administrador del sistema', '{\"all\": true}', NOW()),
(2, 'store_owner', 'Propietario de tienda', '{\"store_management\": true, \"device_management\": true}', NOW()),
(3, 'employee', 'Empleado de tienda', '{\"pos_access\": true, \"sales\": true}', NOW()),
(4, 'customer', 'Cliente', '{\"purchase\": true, \"view_history\": true}', NOW())
ON CONFLICT (id) DO UPDATE SET 
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    permissions = EXCLUDED.permissions;

-- Insertar usuarios de prueba
INSERT INTO \"user\" (id, email, name, password_hash, role_id, created_at) VALUES 
(1, 'admin@smartpay.com', 'Administrador SmartPay', '\$2b\$12\$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxq9S7jG', 1, NOW()),
(2, 'demo@tienda.com', 'Demo Store Owner', '\$2b\$12\$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxq9S7jG', 2, NOW()),
(3, 'empleado@tienda.com', 'Empleado Demo', '\$2b\$12\$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxq9S7jG', 3, NOW())
ON CONFLICT (id) DO UPDATE SET 
    email = EXCLUDED.email,
    name = EXCLUDED.name,
    role_id = EXCLUDED.role_id;

-- Insertar tiendas de prueba
INSERT INTO store (id, name, description, address, city_id, owner_id, plan_id, status, created_at) VALUES 
(1, 'Tienda Demo', 'Tienda de demostración para pruebas', 'Calle 123 #45-67', 1, 2, 2, 'active', NOW()),
(2, 'SuperMercado Central', 'Supermercado en el centro de la ciudad', 'Carrera 7 #12-34', 1, 2, 3, 'active', NOW()),
(3, 'Farmacia San José', 'Farmacia de barrio', 'Calle 45 #23-12', 2, 2, 1, 'active', NOW())
ON CONFLICT (id) DO UPDATE SET 
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    address = EXCLUDED.address,
    city_id = EXCLUDED.city_id,
    owner_id = EXCLUDED.owner_id,
    plan_id = EXCLUDED.plan_id,
    status = EXCLUDED.status;

-- Insertar dispositivos de prueba
INSERT INTO device (id, serial_number, model, store_id, status, last_seen, created_at) VALUES 
(1, 'SP001001', 'SmartPay Terminal v1', 1, 'active', NOW(), NOW()),
(2, 'SP001002', 'SmartPay Terminal v1', 1, 'active', NOW(), NOW()),
(3, 'SP002001', 'SmartPay Terminal v2', 2, 'active', NOW(), NOW()),
(4, 'SP003001', 'SmartPay Mobile', 3, 'active', NOW(), NOW())
ON CONFLICT (id) DO UPDATE SET 
    serial_number = EXCLUDED.serial_number,
    model = EXCLUDED.model,
    store_id = EXCLUDED.store_id,
    status = EXCLUDED.status,
    last_seen = EXCLUDED.last_seen;

-- Insertar pagos de prueba
INSERT INTO payment (id, amount, currency, status, store_id, device_id, customer_email, created_at) VALUES 
(1, 25000.00, 'COP', 'completed', 1, 1, 'cliente1@email.com', NOW() - INTERVAL '1 day'),
(2, 45000.00, 'COP', 'completed', 1, 2, 'cliente2@email.com', NOW() - INTERVAL '2 hours'),
(3, 120000.00, 'COP', 'completed', 2, 3, 'cliente3@email.com', NOW() - INTERVAL '30 minutes'),
(4, 15000.00, 'COP', 'pending', 3, 4, 'cliente4@email.com', NOW() - INTERVAL '5 minutes')
ON CONFLICT (id) DO UPDATE SET 
    amount = EXCLUDED.amount,
    currency = EXCLUDED.currency,
    status = EXCLUDED.status,
    store_id = EXCLUDED.store_id,
    device_id = EXCLUDED.device_id,
    customer_email = EXCLUDED.customer_email;

-- Actualizar secuencias
SELECT setval('country_id_seq', (SELECT MAX(id) FROM country));
SELECT setval('region_id_seq', (SELECT MAX(id) FROM region));
SELECT setval('city_id_seq', (SELECT MAX(id) FROM city));
SELECT setval('plan_id_seq', (SELECT MAX(id) FROM plan));
SELECT setval('role_id_seq', (SELECT MAX(id) FROM role));
SELECT setval('user_id_seq', (SELECT MAX(id) FROM \"user\"));
SELECT setval('store_id_seq', (SELECT MAX(id) FROM store));
SELECT setval('device_id_seq', (SELECT MAX(id) FROM device));
SELECT setval('payment_id_seq', (SELECT MAX(id) FROM payment));
"

echo ""
echo -e "${GREEN}✅ DATOS INSERTADOS EXITOSAMENTE${NC}"
echo ""
echo "Verificando datos insertados:"
docker exec docker-smartpay-db-1 psql -U postgres -d smartpay -c "
SELECT 
    'countries' as tabla, COUNT(*) as registros FROM country
UNION ALL
SELECT 
    'regions' as tabla, COUNT(*) as registros FROM region
UNION ALL
SELECT 
    'cities' as tabla, COUNT(*) as registros FROM city
UNION ALL
SELECT 
    'plans' as tabla, COUNT(*) as registros FROM plan
UNION ALL
SELECT 
    'roles' as tabla, COUNT(*) as registros FROM role
UNION ALL
SELECT 
    'users' as tabla, COUNT(*) as registros FROM \"user\"
UNION ALL
SELECT 
    'stores' as tabla, COUNT(*) as registros FROM store
UNION ALL
SELECT 
    'devices' as tabla, COUNT(*) as registros FROM device
UNION ALL
SELECT 
    'payments' as tabla, COUNT(*) as registros FROM payment;
"

echo ""
echo -e "${GREEN}🚨 POBLACIÓN DE DATOS COMPLETADA 🚨${NC}"
echo "¡LA BASE DE DATOS YA TIENE DATOS!"
