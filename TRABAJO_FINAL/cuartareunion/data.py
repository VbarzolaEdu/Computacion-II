CLUBES = {
    "club_1": {
        "nombre": "Club Pádel del Norte",
        "direccion": "Av. Rivadavia 1234, Buenos Aires",
    },
}

# Todos los clubes tienen estos mismos tipos de canchas.
# La clave compuesta es "club_id:cancha_local" para que sean únicos entre clubes.
CANCHAS = {
    "club_1:cancha_1": {"club_id": "club_1", "nombre": "Cancha 1 - Cubierta Norte",   "tipo": "cubierta",     "precio_por_hora": 3000},
    "club_1:cancha_2": {"club_id": "club_1", "nombre": "Cancha 2 - Cubierta Sur",     "tipo": "cubierta",     "precio_por_hora": 3000},
    "club_1:cancha_3": {"club_id": "club_1", "nombre": "Cancha 3 - Descubierta Este", "tipo": "descubierta",  "precio_por_hora": 2000},
    "club_1:cancha_4": {"club_id": "club_1", "nombre": "Cancha 4 - Descubierta Oeste","tipo": "descubierta",  "precio_por_hora": 2000},
}

# Horarios disponibles: cada hora de 08:00 a 22:00
HORARIOS_DISPONIBLES = [f"{h:02d}:00" for h in range(8, 23)]
