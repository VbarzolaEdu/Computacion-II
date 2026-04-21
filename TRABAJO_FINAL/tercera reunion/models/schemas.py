"""
Schemas de validación para requests/responses.
Usa Pydantic para validación automática.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class ReservaRequest(BaseModel):
    """Schema para request de reserva del cliente"""

    cliente_id: str = Field(..., description="ID del cliente")
    cancha_id: str = Field(..., description="ID de la cancha")
    horario: str = Field(..., description="Horario (formato: HH:MM-HH:MM)")
    precio: float = Field(..., description="Precio de la reserva")
    fecha: Optional[str] = Field(None, description="Fecha (YYYY-MM-DD)")

    class Config:
        schema_extra = {
            "example": {
                "cliente_id": "cliente_001",
                "cancha_id": "cancha_1",
                "horario": "10:00-11:00",
                "precio": 50.0,
                "fecha": "2026-04-20"
            }
        }

    @validator('precio')
    def precio_positivo(cls, v):
        if v <= 0:
            raise ValueError('El precio debe ser positivo')
        return v


class ReservaResponse(BaseModel):
    """Schema para response de reserva confirmada"""

    reserva_id: str
    estado: str
    cliente_id: str
    cancha_id: str
    horario: str
    confirmada_en: datetime

    class Config:
        schema_extra = {
            "example": {
                "reserva_id": "RES-001",
                "estado": "confirmada",
                "cliente_id": "cliente_001",
                "cancha_id": "cancha_1",
                "horario": "10:00-11:00",
                "confirmada_en": "2026-04-16T14:30:00"
            }
        }


class ErrorResponse(BaseModel):
    """Schema para response de error"""

    status: str = "error"
    message: str
    request_id: Optional[str] = None
