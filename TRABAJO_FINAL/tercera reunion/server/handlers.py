"""
Handlers para conexiones de clientes.
Responsable de recibir JSON, validar, y delegar al dispatcher.
"""
import asyncio
import json
import logging
from typing import Any, Dict

from utils.logger import get_logger
from utils.exceptions import ValidationError
from models.schemas import ReservaRequest

logger = get_logger(__name__)


async def handle_client(reader, writer, dispatcher) -> None:
    """
    Maneja una conexión de cliente.

    1. Recibe JSON por TCP
    2. Valida formato
    3. Asigna ID único
    4. Delega al dispatcher
    5. Retorna resultado
    """
    try:
        # Recibir datos del cliente
        data = await reader.readuntil(b'\n')
        request_json = data.decode().strip()
        logger.debug(f"Datos recibidos: {request_json}")

        # Parsear JSON
        request_dict = json.loads(request_json)

        # Validar con schema
        reserva_request = ReservaRequest(**request_dict)

        # Asignar ID único (timestamp + cliente)
        request_id = _generate_request_id()

        # Delegar al dispatcher (esto hace await run_in_executor)
        result = await dispatcher.dispatch(request_id, reserva_request)

        # Enviar respuesta al cliente
        response = {
            "status": "success",
            "id": request_id,
            "data": result
        }

    except json.JSONDecodeError as e:
        logger.error(f"JSON inválido: {e}")
        response = {"status": "error", "message": "JSON inválido"}
    except ValidationError as e:
        logger.error(f"Validación fallida: {e}")
        response = {"status": "error", "message": str(e)}
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        response = {"status": "error", "message": "Error interno del servidor"}

    # Enviar respuesta
    response_json = json.dumps(response) + "\n"
    writer.write(response_json.encode())
    await writer.drain()


def _generate_request_id() -> str:
    """Genera un ID único para cada request"""
    import time
    import random
    timestamp = int(time.time() * 1000)
    random_part = random.randint(1000, 9999)
    return f"{timestamp}-{random_part}"
