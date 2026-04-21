"""
Configuración centralizada de logging.
"""
import logging
import sys
from utils.config import Config


def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger configurado.

    Usa streaming handler por defecto, puede mejorar a file handler.
    """
    config = Config()

    logger = logging.getLogger(name)

    # Solo configurar si no tiene handlers
    if not logger.handlers:
        logger.setLevel(getattr(logging, config.LOG_LEVEL))

        # Handler a stderr
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
