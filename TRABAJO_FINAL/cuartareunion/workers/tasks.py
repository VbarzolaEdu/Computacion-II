import os
import sqlite3
import uuid
from datetime import datetime

from workers.validaciones import validar_reserva

# Conexión SQLite del proceso worker.
# Seteada una sola vez por _init_worker() cuando el proceso arranca.
# Cada proceso worker tiene su propia conexión — SQLite las gestiona de forma independiente.
_conn: sqlite3.Connection | None = None


def _init_worker(db_path: str):
    """
    Función de inicialización del worker.

    ProcessPoolExecutor la llama UNA SOLA VEZ por proceso cuando lo crea.
    Abrimos la conexión SQLite acá para no abrirla en cada request.
    """
    global _conn
    _conn = sqlite3.connect(db_path)
    _conn.execute("PRAGMA journal_mode=WAL")
    _conn.execute("PRAGMA foreign_keys=ON")
    print(f"[worker pid={os.getpid()}] Worker inicializado, DB conectada: {db_path}")


def procesar_reserva(request_dict: dict) -> dict:
    """
    Función principal del worker. Se ejecuta en un proceso separado.

    Valida la solicitud, calcula el precio y confirma la reserva en la DB.
    La UNIQUE constraint de SQLite reemplaza el Lock explícito que teníamos
    antes: si dos workers intentan la misma cancha/fecha/horario al mismo
    tiempo, solo uno hace INSERT exitoso y el otro recibe IntegrityError.
    """
    pid = os.getpid()
    cliente_id = request_dict.get("cliente_id", "?")
    nombre = request_dict.get("nombre", "?")
    cancha_id = request_dict.get("cancha_id", "?")
    horario = request_dict.get("horario", "?")
    fecha = request_dict.get("fecha", "?")

    print(f"[worker pid={pid}] Procesando: cliente={cliente_id} nombre={nombre} cancha={cancha_id} {fecha} {horario}")

    # --- Paso 1: validar cancha y horario en la DB ---
    valida, mensaje_error = validar_reserva(request_dict, _conn)
    if not valida:
        print(f"[worker pid={pid}] Rechazada: {mensaje_error}")
        return {"estado": "rechazada", "mensaje": mensaje_error}

    # --- Paso 2: calcular precio final ---
    # precio_base viene de la tabla canchas, multiplicador de la tabla horarios
    cur = _conn.execute(
        "SELECT c.precio_base, h.multiplicador "
        "FROM canchas c, horarios h "
        "WHERE c.id = ? AND h.horario = ?",
        (cancha_id, horario),
    )
    precio_base, multiplicador = cur.fetchone()
    precio_final = precio_base * multiplicador

    # --- Paso 3: intentar confirmar la reserva ---
    # El INSERT puede fallar con IntegrityError si la UNIQUE constraint
    # (cancha_id, fecha, horario) ya existe → doble reserva.
    reserva_id = str(uuid.uuid4())
    creada_en = datetime.now().isoformat()

    try:
        _conn.execute(
            "INSERT INTO reservas (id, cliente_id, nombre, cancha_id, fecha, horario, precio_final, creada_en) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (reserva_id, cliente_id, nombre, cancha_id, fecha, horario, precio_final, creada_en),
        )
        _conn.commit()
    except sqlite3.IntegrityError:
        print(f"[worker pid={pid}] Rechazada: cancha ocupada (UNIQUE constraint)")
        return {
            "estado": "rechazada",
            "mensaje": f"Cancha '{cancha_id}' no disponible el {fecha} a las {horario}",
        }

    print(f"[worker pid={pid}] Confirmada: id={reserva_id} precio_final=${precio_final:.0f}")
    return {
        "estado": "confirmada",
        "reserva_id": reserva_id,
        "cliente_id": cliente_id,
        "nombre": nombre,
        "cancha_id": cancha_id,
        "horario": horario,
        "fecha": fecha,
        "precio_final": precio_final,
        "mensaje": f"Reserva confirmada para el {fecha} a las {horario}. Total: ${precio_final:.0f}",
    }
