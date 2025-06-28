import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importar routers y la instancia de Socket.IO
from app.api.api import api_router
from app.routers.socket_router import router as socket_router
from app.services.socket_service import sio

# Configuración de la aplicación FastAPI
app = FastAPI(
    title="SmartPay Gateway API",
    description="API Gateway para la comunicación con dispositivos a través de Socket.IO",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Montar la aplicación Socket.IO en la ruta /socket.io
sio_app = socketio.ASGIApp(sio)
app.mount("/socket.io", sio_app)

# Incluir los routers HTTP
app.include_router(api_router)
app.include_router(socket_router)

# Configuración de CORS para permitir solicitudes desde tu frontend
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
