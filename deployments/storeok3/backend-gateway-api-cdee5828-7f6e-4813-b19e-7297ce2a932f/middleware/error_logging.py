import json
import traceback
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.utils.logger import get_logger

logger = get_logger(__name__)


class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para capturar y registrar todos los errores HTTP,
    incluyendo los detalles completos en los logs.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except RequestValidationError as e:
            # Capturar errores de validación (422 Unprocessable Entity)
            error_detail = str(e)
            logger.error(f"Error de validación: {error_detail}", exc_info=True)
            return JSONResponse(
                status_code=422,
                content={"detail": json.loads(e.json())},
            )
        except ValueError as e:
            # Capturar errores de valor, incluyendo problemas de formato de fecha
            error_detail = str(e)
            logger.error(
                f"Error de validación (ValueError): {error_detail}", exc_info=True
            )
            return JSONResponse(
                status_code=422,
                content={"detail": f"Error de validación: {error_detail}"},
            )
        except Exception as e:
            # Capturar cualquier otra excepción no manejada
            error_detail = str(e)
            logger.error(
                f"Error no manejado: {error_detail}\n"
                f"Traceback: {traceback.format_exc()}",
                exc_info=True,
            )
            # Asegurar que el contenido sea serializable a JSON
            # Convertir cualquier objeto de excepción a su representación en string
            return JSONResponse(
                status_code=500,
                content={"detail": f"Error interno del servidor: {error_detail}"},
            )


def setup_error_logging(app: FastAPI) -> None:
    """
    Configura el middleware de logging de errores en la aplicación FastAPI.
    """
    app.add_middleware(ErrorLoggingMiddleware)
