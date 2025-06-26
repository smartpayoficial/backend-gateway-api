from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importar el router de la API
from app.api.api import api_router
from app.routers.socket_router import router as socket_router

# Configuración de la aplicación FastAPI
app = FastAPI(
    title="SmartPay Gateway API",
    description="API Gateway para la comunicación con dispositivos a través de Socket.IO",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Incluir el router principal para exponer /api/v1/*
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
