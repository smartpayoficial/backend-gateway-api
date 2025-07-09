import logging
import os
import sys
from logging.handlers import RotatingFileHandler

# Configuración de directorio de logs
LOG_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs"
)
os.makedirs(LOG_DIR, exist_ok=True)

# Formato de log detallado para incluir la descripción completa de los errores
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
ERROR_FORMAT = (
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s - Exception: %(exc_info)s"
)


def get_logger(name):
    """
    Obtiene un logger configurado con el nombre especificado.

    Args:
        name: Nombre del logger (generalmente __name__ del módulo)

    Returns:
        Un objeto logger configurado
    """
    logger = logging.getLogger(name)

    # Evitar configurar múltiples handlers para el mismo logger
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # Handler para la consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(console_handler)

    # Handler para archivo de logs (rotativo, máximo 10MB, mantener 5 backups)
    file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, "gateway_api.log"),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
    )
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(file_handler)

    # Handler específico para errores con formato detallado
    error_file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, "errors.log"),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(logging.Formatter(ERROR_FORMAT))
    logger.addHandler(error_file_handler)

    return logger
