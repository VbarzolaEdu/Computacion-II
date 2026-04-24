import sqlite3


def validar_reserva(request_dict: dict, conn: sqlite3.Connection) -> tuple[bool, str | None]:
    """
    Valida una solicitud de reserva consultando la base de datos.

    Retorna (True, None) si la cancha y el horario existen y son válidos.
    Retorna (False, "mensaje") si hay algún problema.

    Nota: ya NO verificamos disponibilidad acá. Eso lo maneja el INSERT
    en tasks.py con la UNIQUE constraint. Hacerlo acá (SELECT + INSERT
    separados) volvería a introducir race condition.
    """
    cancha_id = request_dict.get("cancha_id")
    horario = request_dict.get("horario")

    # --- Validación 1: la cancha existe en la DB ---
    cur = conn.execute("SELECT id FROM canchas WHERE id = ?", (cancha_id,))
    if cur.fetchone() is None:
        cur2 = conn.execute("SELECT id FROM canchas")
        ids_validos = ", ".join(r[0] for r in cur2.fetchall())
        return False, f"Cancha '{cancha_id}' no existe. Opciones: {ids_validos}"

    # --- Validación 2: el horario existe en la DB ---
    cur = conn.execute("SELECT horario FROM horarios WHERE horario = ?", (horario,))
    if cur.fetchone() is None:
        cur2 = conn.execute("SELECT horario FROM horarios ORDER BY horario")
        horarios = [r[0] for r in cur2.fetchall()]
        return False, f"Horario '{horario}' no disponible. Opciones: {horarios[0]} a {horarios[-1]}"

    return True, None
