import asyncio
import json
import sqlite3
import time
import uuid

from pydantic import ValidationError

from server.schemas import ReservaRequest


async def handle_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    dispatcher,
    db_path: str,
):
    """
    Maneja la conexión con un cliente TCP.

    Ahora el protocolo soporta dos acciones:
      - "listar_opciones": devuelve clubes, canchas y horarios desde la DB
      - "reservar": valida y procesa la reserva a través del dispatcher/workers

    El campo "accion" en el JSON determina el camino. Si falta, se asume "reservar"
    para mantener compatibilidad con requests anteriores.
    """
    addr = writer.get_extra_info("peername")
    print(f"[handler] Cliente conectado desde {addr}")

    try:
        while True:
            data = await reader.readline()
            if not data:
                print(f"[handler] Cliente {addr} se desconectó")
                break

            # --- Parsear JSON ---
            try:
                payload = json.loads(data.decode("utf-8").strip())
            except json.JSONDecodeError as e:
                await _enviar(writer, {"estado": "error", "mensaje": f"JSON inválido: {e}"})
                continue

            accion = payload.get("accion", "reservar")

            # --- Routing por acción ---
            if accion == "listar_opciones":
                respuesta = _listar_opciones(db_path)
                await _enviar(writer, respuesta)
                continue

            if accion == "reservar":
                await _procesar_reserva(payload, writer, dispatcher, addr)
                continue

            await _enviar(writer, {"estado": "error", "mensaje": f"Acción desconocida: '{accion}'"})

    except (ConnectionResetError, BrokenPipeError):
        print(f"[handler] Conexión con {addr} interrumpida")
    finally:
        writer.close()
        await writer.wait_closed()


async def _procesar_reserva(payload: dict, writer, dispatcher, addr):
    """Valida con Pydantic y despacha al pool de workers."""
    try:
        reserva_req = ReservaRequest(**payload)
    except ValidationError as e:
        await _enviar(writer, {"estado": "error", "mensaje": str(e)})
        return

    timestamp = int(time.time() * 1000)
    request_id = f"req-{timestamp}-{uuid.uuid4().hex[:6]}"
    print(f"[handler] Solicitud {request_id} de {addr}: cancha={reserva_req.cancha_id} horario={reserva_req.horario}")

    resultado = await dispatcher.dispatch(request_id, reserva_req.model_dump())
    await _enviar(writer, resultado)


def _listar_opciones(db_path: str) -> dict:
    """
    Consulta la DB y devuelve clubes, canchas y horarios disponibles.

    Esta es una lectura simple que no necesita pasar por los workers.
    Se ejecuta en el event loop porque es muy rápida (solo SELECTs).
    """
    conn = sqlite3.connect(db_path)
    clubes = [
        {"id": r[0], "nombre": r[1], "direccion": r[2]}
        for r in conn.execute("SELECT id, nombre, direccion FROM clubes ORDER BY id")
    ]
    canchas = [
        {"id": r[0], "club_id": r[1], "nombre": r[2], "tipo": r[3], "precio_base": r[4]}
        for r in conn.execute("SELECT id, club_id, nombre, tipo, precio_base FROM canchas ORDER BY id")
    ]
    horarios = [
        {"horario": r[0], "multiplicador": r[1]}
        for r in conn.execute("SELECT horario, multiplicador FROM horarios ORDER BY horario")
    ]
    conn.close()
    return {"accion": "opciones", "clubes": clubes, "canchas": canchas, "horarios": horarios}


async def _enviar(writer: asyncio.StreamWriter, datos: dict):
    """Serializa el dict a JSON y lo envía terminado en newline."""
    linea = json.dumps(datos, ensure_ascii=False) + "\n"
    writer.write(linea.encode("utf-8"))
    await writer.drain()
