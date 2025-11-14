# server_processing.py
import argparse
import socket
import json
from multiprocessing import Pool

from common.serialization import send_packet, recv_packet
from processor.screenshot import take_screenshot
from processor.performance import analyze_performance


def process_request(data):
    """
    Ejecuta el procesamiento CPU-bound en un worker del Pool.
    """
    url = data.get("url")
    html = data.get("html")

    screenshot = take_screenshot(url)
    performance = analyze_performance(html)

    return {
        "screenshot": screenshot,
        "performance": performance,
        "status": "ok"
    }


def start_server(host, port, workers):
    """
    Servidor TCP dual-stack IPv4 + IPv6 con multiprocessing.
    """
    # Socket IPv6 que también acepta IPv4
    server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    server.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
    server.bind((host, port))
    server.listen()

    print(f"[Servidor B] Escuchando en [{host}]:{port} con {workers} workers")

    pool = Pool(processes=workers)

    while True:
        conn, addr = server.accept()
        print(f"[Servidor B] Conexión desde {addr}")

        request = recv_packet(conn)     # <-- integración correcta
        result = pool.apply(process_request, (request,))

        send_packet(conn, result)       # <-- integración correcta
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Servidor B - Procesamiento")
    parser.add_argument("--ip", default="::")
    parser.add_argument("--port", type=int, default=9000)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    start_server(args.ip, args.port, args.workers)
