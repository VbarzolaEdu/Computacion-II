"""
Cliente interactivo de reservas de pádel.

Uso:
  python3 cliente.py                        # IPv4, 127.0.0.1:8888
  python3 cliente.py --ipv6                 # IPv6, ::1:8888
  python3 cliente.py --host 192.168.1.5 --port 9000
"""

import argparse
import json
import socket
from datetime import date, timedelta


def parse_args():
    parser = argparse.ArgumentParser(description="Cliente de reservas de pádel")
    parser.add_argument("--host", default=None, help="IP del servidor (default: 127.0.0.1 / ::1 con --ipv6)")
    parser.add_argument("--port", type=int, default=8888, help="Puerto del servidor (default: 8888)")
    grupo = parser.add_mutually_exclusive_group()
    grupo.add_argument("--ipv4", action="store_true", help="Usar IPv4 (default)")
    grupo.add_argument("--ipv6", action="store_true", help="Usar IPv6")
    return parser.parse_args()


def conectar(host: str | None, port: int, usar_ipv6: bool) -> tuple[socket.socket, str]:
    """Crea el socket TCP y se conecta al servidor."""
    if usar_ipv6:
        family = socket.AF_INET6
        host = host or "::1"
    else:
        family = socket.AF_INET
        host = host or "127.0.0.1"

    print(f"\nConectando a {host}:{port} ({'IPv6' if usar_ipv6 else 'IPv4'})...")
    sock = socket.socket(family, socket.SOCK_STREAM)
    sock.connect((host, port))
    print("Conectado.\n")
    return sock, host


def enviar_y_recibir(sock: socket.socket, datos: dict) -> dict:
    """Envía un dict como JSON al servidor y devuelve la respuesta."""
    sock.sendall((json.dumps(datos, ensure_ascii=False) + "\n").encode("utf-8"))
    # recv con buffer grande para respuestas con listas (listar_opciones)
    respuesta = b""
    while not respuesta.endswith(b"\n"):
        respuesta += sock.recv(65536)
    return json.loads(respuesta.decode("utf-8").strip())


def elegir(opciones: list, titulo: str, formatter) -> object:
    """Muestra una lista numerada y pide al usuario que elija una opción."""
    print(f"\n{titulo}:")
    for i, op in enumerate(opciones, 1):
        print(f"  [{i}] {formatter(op)}")
    while True:
        try:
            idx = int(input("  Selección: ")) - 1
            if 0 <= idx < len(opciones):
                return opciones[idx]
        except (ValueError, KeyboardInterrupt):
            pass
        print("  Opción inválida, intentá de nuevo.")


def elegir_fecha() -> str:
    """Muestra los próximos 7 días y permite elegir uno."""
    hoy = date.today()
    fechas = [hoy + timedelta(days=i) for i in range(1, 8)]
    DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

    elegida = elegir(
        fechas,
        "Fecha de la reserva",
        lambda f: f"{DIAS[f.weekday()]} {f.strftime('%d/%m/%Y')}",
    )
    return elegida.isoformat()


def main():
    args = parse_args()

    try:
        sock, host = conectar(args.host, args.port, args.ipv6)
    except (ConnectionRefusedError, OSError) as e:
        print(f"Error al conectar: {e}")
        print("¿Está el servidor corriendo?")
        return

    try:
        # --- Pedir opciones al servidor ---
        print("Obteniendo opciones del servidor...")
        opciones = enviar_y_recibir(sock, {"accion": "listar_opciones"})
        clubes   = opciones["clubes"]
        canchas  = opciones["canchas"]
        horarios = opciones["horarios"]

        print("=" * 48)
        print("     RESERVA DE CANCHA DE PÁDEL")
        print("=" * 48)

        # --- Datos del cliente ---
        nombre     = input("\nTu nombre completo: ").strip()
        cliente_id = input("Tu ID de cliente:   ").strip()
        if not nombre or not cliente_id:
            print("Nombre e ID son obligatorios.")
            return

        # --- Elegir club (si hay más de uno se muestra menú, si no se usa el único) ---
        if len(clubes) == 1:
            club = clubes[0]
            print(f"\nClub: {club['nombre']}  —  {club['direccion']}")
        else:
            club = elegir(
                clubes,
                "Club",
                lambda c: f"{c['nombre']}  —  {c['direccion']}",
            )

        # --- Elegir cancha (solo las del club seleccionado) ---
        canchas_del_club = [c for c in canchas if c["club_id"] == club["id"]]
        cancha = elegir(
            canchas_del_club,
            "Cancha disponible",
            lambda c: f"{c['nombre']}  ({c['tipo']})  ${c['precio_base']}/h",
        )

        # --- Elegir fecha ---
        fecha = elegir_fecha()

        # --- Elegir horario (muestra precio calculado y marca los pico) ---
        def formato_horario(h):
            precio = cancha["precio_base"] * h["multiplicador"]
            pico   = "  ⚡ horario pico" if h["multiplicador"] > 1 else ""
            return f"{h['horario']}   ${precio:.0f}{pico}"

        horario = elegir(horarios, "Horario", formato_horario)

        precio_estimado = cancha["precio_base"] * horario["multiplicador"]

        # --- Resumen antes de confirmar ---
        print(f"\n{'=' * 48}")
        print("  RESUMEN DE RESERVA")
        print(f"{'=' * 48}")
        print(f"  Nombre:   {nombre}")
        print(f"  ID:       {cliente_id}")
        print(f"  Club:     {club['nombre']}")
        print(f"  Cancha:   {cancha['nombre']}")
        print(f"  Fecha:    {fecha}")
        print(f"  Horario:  {horario['horario']}")
        print(f"  Precio:   ${precio_estimado:.0f}")
        print(f"{'=' * 48}")

        confirmar = input("\n¿Confirmar reserva? [s/N]: ").strip().lower()
        if confirmar != "s":
            print("Reserva cancelada.")
            return

        # --- Enviar reserva al servidor ---
        respuesta = enviar_y_recibir(sock, {
            "accion":     "reservar",
            "cliente_id": cliente_id,
            "nombre":     nombre,
            "cancha_id":  cancha["id"],
            "horario":    horario["horario"],
            "fecha":      fecha,
        })

        # --- Mostrar resultado ---
        print()
        if respuesta.get("estado") == "confirmada":
            print(f"✓ {respuesta['mensaje']}")
            print(f"  ID de reserva: {respuesta['reserva_id']}")
        else:
            print(f"✗ Reserva rechazada: {respuesta.get('mensaje', 'error desconocido')}")

    except KeyboardInterrupt:
        print("\nCancelado.")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
