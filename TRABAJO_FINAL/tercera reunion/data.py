from datetime import datetime, timedelta

# Estructura simple para empezar
CANCHAS = {
    "cancha_1": {"nombre": "Cancha A", "tipo": "futbol", "precio_por_hora": 50, "ubicacion": "Zona Norte"},
    "cancha_2": {"nombre": "Cancha B", "tipo": "futbol", "precio_por_hora": 50, "ubicacion": "Zona Centro"},
    "cancha_3": {"nombre": "Cancha C", "tipo": "tenis", "precio_por_hora": 60, "ubicacion": "Zona Sur"},
}

HORARIOS_DISPONIBLES = ["08:00", "09:00", "10:00", "11:00", "12:00" , "13:00", "14:00", "15:00", "16:00", "17:00"]  # Horas disponibles

# Generar fechas disponibles para los próximos 7 días
FECHAS_DISPONIBLES = [(datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(1, 8)]


def get_precio_cancha(cancha_id: str) -> float:
    """Obtiene el precio por hora de una cancha"""
    if cancha_id in CANCHAS:
        return CANCHAS[cancha_id]["precio_por_hora"]
    return 0.0
