# Sistema de Deployment Automático para Tiendas

Este sistema permite desplegar automáticamente instancias independientes del backend y base de datos para cada tienda registrada en el sistema.

## Características

- **Deployment automático**: Crea una instancia única del backend y DB para cada tienda
- **Puertos únicos**: Genera puertos únicos basados en el ID de la tienda para evitar conflictos
- **Gestión completa**: Deploy, estado y undeploy de instancias
- **Persistencia**: Guarda los links de acceso en la base de datos
- **Aislamiento**: Cada tienda tiene su propia red Docker y configuración

## Endpoints Disponibles

### 1. Crear y desplegar tienda automáticamente (NUEVO)
```http
POST /api/v1/stores/
```

**Descripción**: Crea una nueva tienda y la despliega automáticamente con su propio backend y DB.

**Body de la petición**:
```json
{
  "nombre": "Mi Tienda",
  "country_id": "uuid-del-país",
  "tokens_disponibles": 500,
  "plan": "premium"
}
```

**Respuesta exitosa**:
```json
{
  "message": "Tienda creada y deployment completado exitosamente",
  "store": {
    "id": "uuid-de-la-tienda",
    "nombre": "Mi Tienda",
    "country_id": "uuid-del-país",
    "plan": "premium",
    "tokens_disponibles": 500,
    "created_at": "2024-01-01T12:00:00",
    "back_link": "http://localhost:9123",
    "db_link": "http://localhost:9125"
  },
  "deployment": {
    "back_link": "http://localhost:9123",
    "db_link": "http://localhost:9125",
    "ports": {
      "backend_port": 9123,
      "websocket_port": 9124,
      "db_port": 9125
    },
    "status": "deployed"
  }
}
```

### 2. Desplegar una tienda existente
```http
POST /api/v1/stores/{store_id}/deploy
```

**Descripción**: Despliega automáticamente una versión del backend y DB para una tienda que ya existe.

**Respuesta exitosa**:
```json
{
  "message": "Deployment completado exitosamente",
  "store_id": "uuid-de-la-tienda",
  "back_link": "http://localhost:9123",
  "db_link": "http://localhost:9125",
  "ports": {
    "backend_port": 9123,
    "websocket_port": 9124,
    "db_port": 9125
  },
  "status": "deployed"
}
```

### 3. Obtener estado del deployment
```http
GET /api/v1/stores/{store_id}/deploy/status
```

**Descripción**: Obtiene el estado actual del deployment de una tienda.

**Respuesta**:
```json
{
  "store_id": "uuid-de-la-tienda",
  "status": "running",
  "backend_exists": true,
  "db_exists": true,
  "containers_running": true,
  "ports": {
    "backend_port": 9123,
    "websocket_port": 9124,
    "db_port": 9125
  },
  "paths": {
    "backend_path": "/path/to/deployments/backend-gateway-api-{store_id}",
    "db_path": "/path/to/deployments/db-smartpay-{store_id}"
  },
  "back_link": "http://localhost:9123",
  "db_link": "http://localhost:9125"
}
```

**Estados posibles**:
- `not_deployed`: No hay deployment para esta tienda
- `running`: Deployment activo y contenedores corriendo
- `stopped`: Deployment existe pero contenedores detenidos
- `error`: Error obteniendo el estado

### 4. Eliminar deployment
```http
DELETE /api/v1/stores/{store_id}/deploy
```

**Descripción**: Detiene y elimina completamente el deployment de una tienda.

**Respuesta**:
```json
{
  "message": "Undeploy completado exitosamente",
  "store_id": "uuid-de-la-tienda",
  "status": "undeployed"
}
```

## Funcionamiento Interno

### Generación de Puertos
Los puertos se generan usando un hash del `store_id` para garantizar unicidad:
- Puerto base = 9000 + (hash(store_id) % 1000)
- Backend: puerto_base
- WebSocket: puerto_base + 1
- DB: puerto_base + 2

### Estructura de Directorios
```
/home/danielamg/Escritorio/trabajo/olimpo/smart-pay/deployments/
├── backend-gateway-api-{store_id}/
│   ├── app/
│   ├── docker/
│   ├── docker-compose.yml (personalizado)
│   └── ... (copia completa del backend)
└── db-smartpay-{store_id}/
    └── ... (copia completa de la DB)
```

### Configuración Docker
Cada deployment genera un `docker-compose.yml` personalizado con:
- Nombres de contenedor únicos
- Puertos únicos
- Red Docker aislada
- Variables de entorno específicas para la tienda

## Requisitos

1. **Docker y Docker Compose** instalados
2. **Permisos de escritura** en el directorio de deployments
3. **Puertos disponibles** en el rango 9000-9999
4. **Rutas base existentes**:
   - `/home/danielamg/Escritorio/trabajo/olimpo/smart-pay/backend-gateway-api`
   - `/home/danielamg/Escritorio/trabajo/olimpo/smart-pay/db-smartpay` (opcional)

## Ejemplos de Uso

### Usando curl

1. **Crear y desplegar tienda automáticamente**:
```bash
curl -X POST "http://localhost:8000/api/v1/stores/" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Mi Nueva Tienda",
    "country_id": "uuid-del-país",
    "tokens_disponibles": 500,
    "plan": "premium"
  }'
```

2. **Desplegar una tienda existente**:
```bash
curl -X POST "http://localhost:8000/api/v1/stores/{store_id}/deploy" \
  -H "Content-Type: application/json"
```

3. **Verificar estado**:
```bash
curl -X GET "http://localhost:8000/api/v1/stores/{store_id}/deploy/status"
```

4. **Eliminar deployment**:
```bash
curl -X DELETE "http://localhost:8000/api/v1/stores/{store_id}/deploy"
```

### Usando Python
```python
import requests

store_id = "tu-store-id-aqui"
base_url = "http://localhost:8000/api/v1/stores"

# Desplegar
response = requests.post(f"{base_url}/{store_id}/deploy")
deployment_info = response.json()
print(f"Backend disponible en: {deployment_info['back_link']}")

# Verificar estado
status_response = requests.get(f"{base_url}/{store_id}/deploy/status")
status = status_response.json()
print(f"Estado: {status['status']}")

# Eliminar deployment
undeploy_response = requests.delete(f"{base_url}/{store_id}/deploy")
print("Deployment eliminado")
```

## Monitoreo y Logs

Los logs del sistema de deployment se encuentran en:
- Logs del backend principal: `/home/danielamg/Escritorio/trabajo/olimpo/smart-pay/backend-gateway-api/logs/`
- Logs de cada deployment: `{deployment_path}/logs/`

## Troubleshooting

### Error: "Puerto ya en uso"
- Verificar que no hay otros servicios usando los puertos generados
- Usar el endpoint de estado para verificar deployments existentes

### Error: "No se puede copiar archivos"
- Verificar permisos de escritura en el directorio de deployments
- Verificar que las rutas base existen

### Error: "Docker compose falló"
- Verificar que Docker está corriendo
- Revisar logs del deployment específico
- Verificar que no hay conflictos de nombres de contenedor

### Limpieza manual
Si necesitas limpiar deployments manualmente:
```bash
# Detener todos los contenedores de una tienda
docker stop backend-api-{store_id}

# Eliminar contenedores
docker rm backend-api-{store_id}

# Eliminar archivos
rm -rf /home/danielamg/Escritorio/trabajo/olimpo/smart-pay/deployments/backend-gateway-api-{store_id}
rm -rf /home/danielamg/Escritorio/trabajo/olimpo/smart-pay/deployments/db-smartpay-{store_id}
```

## Notas Importantes

1. **Recursos**: Cada deployment consume recursos del sistema (CPU, memoria, almacenamiento)
2. **Puertos**: El sistema puede manejar hasta 1000 tiendas simultáneas (puertos 9000-9999)
3. **Backup**: Los deployments no incluyen backup automático de datos
4. **Actualizaciones**: Para actualizar un deployment, debe eliminarse y recrearse
5. **Seguridad**: Los deployments usan la misma configuración SSL del backend principal
