"""
Tareas que ejecutan los workers.
Estas funciones se ejecutan en procesos separados (no asyncio).
"""
import logging
from typing import Any, Dict

from utils.logger import get_logger
from workers.validation import validar_reserva
from database.queries import guardar_reserva

logger = get_logger(__name__)


def procesar_reserva(request_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Función principal que ejecuta cada worker.
    Se ejecuta en proceso separado (bloqueante es OK aquí).

    Pasos:
    1. Validar cancha, horario, disponibilidad
    2. Guardar en BD
    3. Retornar confirmación
    """
    from datetime import datetime

    logger.info(f"Worker procesando reserva: {request_dict.get('cliente_id')}")

    try:
        # Validar
        validar_reserva(request_dict)

        # Guardar en BD
        reserva_id = guardar_reserva(request_dict)

        result = {
            "reserva_id": reserva_id,
            "estado": "confirmada",
            "confirmada_en": datetime.now().isoformat(),
            "mensaje": "Reserva guardada exitosamente"
        }

        logger.info(f"Reserva procesada: {reserva_id}")
        return result

    except Exception as e:
        logger.error(f"Error procesando reserva: {e}")
        return {
            "estado": "error",
            "mensaje": str(e)
        }
