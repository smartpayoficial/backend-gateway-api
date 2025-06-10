import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importar el router de la API
from app.api.api import api_router

# Importar el módulo de socket
from app.servicios.socket import (
    connect,
    disconnect,
    get_active_connections,
    message,
    print_connections,
    sio,
)

# Importar el manejador de joinRoom
from app.socketio_app import handle_join_room

# Configuración de la aplicación FastAPI
app = FastAPI(
    title="SmartPay Gateway API",
    description="API Gateway para la comunicación con dispositivos a través de Socket.IO",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir los routers de la API
app.include_router(api_router, prefix="/api")

print("Inicializando Socket.IO...")

# Configurar manejadores de eventos Socket.IO
sio.on("connect", connect)
sio.on("disconnect", disconnect)
sio.on("message", message)
sio.on("joinRoom", handler=handle_join_room)  # Registrar el manejador joinRoom

# Configurar opciones de CORS en la aplicación FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear aplicación ASGI para Socket.IO
socket_app = socketio.ASGIApp(sio, socketio_path="/socket.io")

# Montar la aplicación de Socket.IO en FastAPI
app.mount("", socket_app)

print("Aplicación Socket.IO configurada correctamente")

# Obtener conexiones activas
active_connections = get_active_connections()

# Verificar manejadores registrados
print("\n=== VERIFICACIÓN DE MANEJADORES REGISTRADOS ===")
print(f"[SOCKET.IO] Manejadores registrados: {sio.handlers}")

# Verificar conexiones activas
print("\n=== CONEXIONES ACTIVAS ===")
print_connections()


# Endpoint raíz
@app.get("/")
async def root():
    """
    Endpoint raíz.

    Proporciona información básica sobre la API y enlaces útiles.
    """
    return {
        "service": "SmartPay Gateway API",
        "status": "running",
        "version": "1.0.0",
        "documentation": "/docs",
        "socketio_endpoint": "/socket.io",
        "api_endpoints": {
            "health_check": "/api/v1/health",
            "connections": "/api/v1/connections",
            "broadcast": "/api/v1/broadcast",
        },
    }
