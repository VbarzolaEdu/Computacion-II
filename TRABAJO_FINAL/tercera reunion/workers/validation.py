"""
Validaciones de negocio para las reservas.
Se ejecutan en los workers.
"""
import logging
from typing import Any, Dict

from utils.logger import get_logger
from utils.exceptions import ValidationError
from data import CANCHAS, HORARIOS_DISPONIBLES, get_precio_cancha

logger = get_logger(__name__)


def validar_reserva(request_dict: Dict[str, Any]) -> None:
    """
    Valida una reserva antes de guardarla.

    Checks:
    - Cancha existe
    - Horario es válido
    - Disponibilidad (no hay conflictos)
    - Precio es consistente
    """

    cancha_id = request_dict.get("cancha_id")
    horario = request_dict.get("horario")
    precio = request_dict.get("precio")

    # Validar cancha
    if not cancha_id:
        raise ValidationError("cancha_id es requerido")

    if not _cancha_existe(cancha_id):
        raise ValidationError(f"Cancha {cancha_id} no existe")

    # Validar horario
    if not horario:
        raise ValidationError("horario es requerido")

    if not _horario_valido(horario):
        raise ValidationError("horario inválido")

    # Validar disponibilidad
    if not _cancha_disponible(cancha_id, horario):
        raise ValidationError(f"Cancha {cancha_id} no disponible en ese horario")

    # Validar precio
    precio_esperado = _obtener_precio_cancha(cancha_id)
    if precio != precio_esperado:
        raise ValidationError(f"Precio incorrecto (esperado: {precio_esperado})")

    logger.info(f"Validación exitosa para cancha {cancha_id}")


def _cancha_existe(cancha_id: str) -> bool:
    """Verifica si la cancha existe en BD"""
    return cancha_id in CANCHAS


def _horario_valido(horario: str) -> bool:
    """Verifica si el horario tiene formato válido"""
    return horario in HORARIOS_DISPONIBLES


def _cancha_disponible(cancha_id: str, horario: str) -> bool:
    """Verifica si la cancha está disponible en ese horario"""
    # TODO: consultar conflictos en BD
    return True


def _obtener_precio_cancha(cancha_id: str) -> float:
    """Obtiene el precio actual de la cancha"""
    return get_precio_cancha(cancha_id)
