from datetime import date

from pydantic import BaseModel, field_validator


class ReservaRequest(BaseModel):
    """
    Estructura del JSON que envía el cliente.

    Pydantic valida automáticamente los tipos y ejecuta los validators.
    Si algo falla, lanza ValidationError con mensajes claros.
    """

    cliente_id: str
    nombre: str        # nombre completo del cliente
    cancha_id: str
    horario: str       # formato "HH:MM"
    fecha: str         # formato "YYYY-MM-DD"

    @field_validator("horario")
    @classmethod
    def horario_tiene_formato_correcto(cls, v: str) -> str:
        partes = v.split(":")
        if len(partes) != 2 or not partes[0].isdigit() or not partes[1].isdigit():
            raise ValueError("horario debe tener formato HH:MM (ej: '09:00')")
        return v

    @field_validator("fecha")
    @classmethod
    def fecha_tiene_formato_correcto(cls, v: str) -> str:
        try:
            date.fromisoformat(v)
        except ValueError:
            raise ValueError("fecha debe tener formato YYYY-MM-DD (ej: '2026-04-25')")
        return v
