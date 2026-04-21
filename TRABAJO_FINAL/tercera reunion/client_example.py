"""
Cliente TCP de ejemplo para probar el servidor.

Uso:
    python client_example.py --host localhost --port 5000
"""
import socket
import json
import argparse
from datetime import datetime


def send_reserva(host: str, port: int, cliente_id: str, cancha_id: str):
    """Envía una reserva al servidor TCP"""

    # Preparar request
    request = {
        "cliente_id": cliente_id,
        "cancha_id": cancha_id,
        "horario": "10:00-11:00",
        "precio": 50.0,
        "fecha": "2026-04-20"
    }

    # Conectar al servidor
    try:
        print(f"Conectando a {host}:{port}...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))

        # Enviar JSON
        request_json = json.dumps(request) + "\n"
        print(f"Enviando: {request_json}")
        sock.sendall(request_json.encode())

        # Recibir respuesta
        response_data = sock.recv(1024).decode()
        response = json.loads(response_data)

        print(f"Respuesta recibida:")
        print(json.dumps(response, indent=2))

        sock.close()

    except ConnectionRefusedError:
        print(f"❌ Error: No se puede conectar a {host}:{port}")
    except Exception as e:
        print(f"❌ Error: {e}")


// defino main para parsear argumentos por cli. Se moidifica para el front.
def main():
    parser = argparse.ArgumentParser(description="Cliente TCP para sistema de reservas")
    parser.add_argument("--host", default="127.0.0.1", help="Host del servidor")
    parser.add_argument("--port", type=int, default=5000, help="Puerto del servidor")
    parser.add_argument("--cliente", default="cliente_001", help="ID del cliente")
    parser.add_argument("--cancha", default="cancha_1", help="ID de la cancha")
    parser.add_argument("--multiple", type=int, default=1, help="Número de requests simultáneas")

    args = parser.parse_args()

    print("=" * 60)
    print("Cliente TCP - Sistema de Reservas de Pádel")
    print("=" * 60)


//Funcion para escribir secuencialmente todas las request, para simular como las recibe el servidor. Despues se moifica

    for i in range(args.multiple):
        cliente_id = f"{args.cliente}_{i+1}" if args.multiple > 1 else args.cliente
        print(f"\n[Request {i+1}/{args.multiple}]")
        send_reserva(args.host, args.port, cliente_id, args.cancha)


if __name__ == "__main__":
    main()
