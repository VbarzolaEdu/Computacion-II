"""
Modelo de dominio: Reserva
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Reserva:
    """Representa una reserva de pádel"""

    id: str
    cliente_id: str
    cancha_id: str
    horario: str
    fecha: str
    precio: float
    estado: str  # "confirmada", "cancelada", "pendiente"
    creada_en: datetime
    confirmada_en: Optional[datetime] = None

    def __post_init__(self):
        if self.precio <= 0:
            raise ValueError("El precio debe ser positivo")


@dataclass
class Cancha:
    """Representa una cancha de pádel"""

    id: str
    nombre: str
    precio_por_hora: float
    disponible: bool
    ubicacion: str

    def __post_init__(self):
        if self.precio_por_hora <= 0:
            raise ValueError("El precio debe ser positivo")
