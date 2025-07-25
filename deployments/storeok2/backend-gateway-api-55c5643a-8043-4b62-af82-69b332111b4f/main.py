import socketio
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.api import api_router
from app.middleware.error_logging import setup_error_logging
from app.routers.socket_router import router as socket_router
from app.services.socket_service import sio
from app.utils.logger import get_logger

# Configurar el logger principal
logger = get_logger(__name__)

# Importar routers y la instancia de Socket.IO


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

# Configurar el middleware de logging de errores
setup_error_logging(app)


# Manejador personalizado para errores de validación (422 Unprocessable Entity)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Procesar los errores para asegurar que sean serializables a JSON
    error_detail = []
    for err in exc.errors():
        # Crear una copia del error sin referencias a objetos no serializables
        error_dict = {
            "type": err.get("type", ""),
            "loc": err.get("loc", []),
            "msg": err.get("msg", ""),
            "input": err.get("input", None),
        }
        # Si hay un contexto con un error, extraer solo el mensaje del error
        if (
            "ctx" in err
            and "error" in err["ctx"]
            and hasattr(err["ctx"]["error"], "__str__")
        ):
            error_dict["ctx"] = {"error": str(err["ctx"]["error"])}
        error_detail.append(error_dict)

    logger.error(f"Error de validación: {error_detail}", exc_info=True)
    return JSONResponse(
        status_code=422,
        content={"detail": error_detail},
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
