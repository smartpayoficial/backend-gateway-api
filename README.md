# Backend SmartPay

Una API FastAPI para SmartPay con soporte para WebSockets y funcionalidad de broadcast de mensajes.

## Características

- ✅ **Health Check** - Endpoint de verificación de estado
- 🔌 **WebSockets** - Conexiones en tiempo real para dispositivos
- 📡 **Broadcast** - Envío de mensajes a todos los dispositivos conectados
- 🐳 **Docker** - Contenarización completa
- 🔧 **Pre-commit** - Hooks de calidad de código

## Endpoints Disponibles

### HTTP Endpoints
- `GET /` - Health check con contador de dispositivos conectados
- `POST /broadcast` - Enviar mensaje a todos los dispositivos conectados
- `GET /connections` - Información sobre conexiones WebSocket activas
- `GET /docs` - Documentación interactiva de la API

### WebSocket Endpoints
- `WS /ws/{device_id}` - Conexión WebSocket para dispositivos

## Pasos de Ejecución

### Opción 1: Usando Docker (Recomendado)
1. Navegar al directorio docker:
   ```bash
   cd docker
   ```
2. Ejecutar con Docker Compose:
   ```bash
   sudo docker-compose up --build
   ```

### Opción 2: Usando Python Virtual Environment
1. Ejecutar el script de configuración:
   ```bash
   chmod +x setup_env.sh
   ./setup_env.sh
   ```
2. Activar el entorno virtual:
   ```bash
   source venv/bin/activate
   ```
3. Ejecutar el servidor FastAPI:
   ```bash
   uvicorn app.main:app --reload
   ```

## URLs de Acceso

- **API:** `http://localhost:8004`
- **Documentación:** `http://localhost:8004/docs`
- **Cliente WebSocket de prueba:** Abrir `websocket_test.html` en el navegador

## Uso de WebSockets

### Conectar un dispositivo
```javascript
const ws = new WebSocket('ws://localhost:8004/ws/mi_dispositivo');
```

### Enviar mensaje broadcast (HTTP)
```bash
curl -X POST http://localhost:8004/broadcast \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola dispositivos!", "device_id": "servidor"}'
```

### Verificar conexiones activas
```bash
curl http://localhost:8004/connections
```

## Desarrollo

### Pre-commit
Para instalar los hooks de pre-commit:
```bash
pre-commit install
```

Para ejecutar checks en todos los archivos:
```bash
pre-commit run --all-files
```

## Estructura del Proyecto

```
BackendSmartPay/
├── app/
│   ├── __init__.py
│   └── main.py              # Aplicación principal con WebSockets
├── docker/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── docker-compose.yml   # Configuración de Docker
├── .pre-commit-config.yaml  # Configuración de pre-commit
├── setup_env.sh            # Script de configuración
├── websocket_test.html     # Cliente de prueba WebSocket
└── README.md
```
