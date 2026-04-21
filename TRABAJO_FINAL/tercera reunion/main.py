"""
Entry point principal de la aplicación.
Inicia el servidor asyncio.
"""
import asyncio
import sys
import logging
import argparse
import os

from server.servidor import AsyncioServer
from utils.config import Config
from utils.logger import get_logger

logger = get_logger(__name__)


def parse_args():
    """Parsea argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(
        description="Sistema de Reservas de Pádel"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Número de workers (por defecto: 4 o valor de env NUM_WORKERS)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default=None,
        help="Host del servidor (por defecto: 127.0.0.1 o valor de env SERVER_HOST)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Puerto del servidor (por defecto: 5000 o valor de env SERVER_PORT)"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default=None,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Nivel de logging (por defecto: INFO o valor de env LOG_LEVEL)"
    )
    
    return parser.parse_args()


async def main():
    """Punto de entrada"""
    args = parse_args()
    
    # Aplicar argumentos CLI a variables de entorno (CLI tiene prioridad)
    if args.workers is not None:
        os.environ["NUM_WORKERS"] = str(args.workers)
    if args.host is not None:
        os.environ["SERVER_HOST"] = args.host
    if args.port is not None:
        os.environ["SERVER_PORT"] = str(args.port)
    if args.log_level is not None:
        os.environ["LOG_LEVEL"] = args.log_level
    
    config = Config()

    logger.info("=" * 60)
    logger.info("Sistema de Reservas de Pádel - Iniciando")
    logger.info(f"Host: {config.HOST}")
    logger.info(f"Puerto: {config.PORT}")
    logger.info(f"Workers: {config.NUM_WORKERS}")
    logger.info("=" * 60)

    server = AsyncioServer(config)

    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("\nInterrupción del usuario detectada")
    except Exception as e:
        logger.error(f"Error fatal: {e}", exc_info=True)
        sys.exit(1)
    finally:
        await server.stop()
        logger.info("Aplicación terminada")


if __name__ == "__main__":
    asyncio.run(main())
