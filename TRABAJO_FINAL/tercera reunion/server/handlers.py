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
from utils.reserva_logger import get_reserva_logger

logger = get_logger(__name__)
reserva_logger = get_reserva_logger()


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

        # Enviar respuesta al cliente con el formato esperado
        if result.get("estado") == "error":
            response = {
                "estado": "error",
                "message": result.get("mensaje", "Error desconocido")
            }
            # Loguear reserva rechazada
            reserva_logger.log_reserva_rechazada(
                request_dict,
                result.get("mensaje", "Error desconocido")
            )
        else:
            response = {
                "estado": "confirmada",
                "reserva_id": result.get("reserva_id"),
                "cancha_id": request_dict.get("cancha_id"),
                "horario": request_dict.get("horario"),
                "confirmada_en": result.get("confirmada_en"),
                "message": "Reserva confirmada exitosamente"
            }
            # Loguear reserva confirmada en JSON
            reserva_logger.log_reserva_confirmada({
                "reserva_id": result.get("reserva_id"),
                "cliente_id": request_dict.get("cliente_id"),
                "cancha_id": request_dict.get("cancha_id"),
                "horario": request_dict.get("horario"),
                "precio": request_dict.get("precio"),
                "fecha": request_dict.get("fecha"),
                "confirmada_en": result.get("confirmada_en")
            })

    except json.JSONDecodeError as e:
        logger.error(f"JSON inválido: {e}")
        response = {"estado": "error", "message": "JSON inválido"}
    except ValidationError as e:
        logger.error(f"Validación fallida: {e}")
        response = {"estado": "error", "message": str(e)}
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        response = {"estado": "error", "message": "Error desconocido"}

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
