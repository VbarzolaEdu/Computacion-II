# server_scraping.py
# server_scraping.py
import argparse
import json
import socket
import aiohttp
from aiohttp import web

from scraper.html_parser import parse_html
from common.serialization import send_packet, recv_packet


def connect_to_processing_server(host, port):
    """
    Resuelve automáticamente IPv4 o IPv6 usando getaddrinfo.
    """
    infos = socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM)

    for family, socktype, proto, canonname, sockaddr in infos:
        try:
            s = socket.socket(family, socktype, proto)
            s.connect(sockaddr)
            return s
        except Exception:
            continue

    raise RuntimeError("❌ No se pudo conectar al Servidor B.")


async def handle_scrape(request):
    url = request.rel_url.query.get("url")
    if not url:
        return web.json_response({"error": "Missing URL"}, status=400)

    # 1. Obtener HTML con aiohttp (asincrónico)
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                html = await resp.text()
        except Exception as e:
            return web.json_response({"error": f"No se pudo obtener la URL: {e}"}, status=500)

    # 2. Scraping local
    scraping_data = parse_html(html)

    # 3. Enviar datos a Servidor B
    sock = connect_to_processing_server(request.app["b_host"], request.app["b_port"])

    payload = {
        "url": url,
        "html": html,
        "scraping_data": scraping_data
    }

    send_packet(sock, payload)     # <-- integración correcta
    response = recv_packet(sock)   # <-- integración correcta
    sock.close()

    # 4. Respuesta final
    return web.json_response({
        "url": url,
        "scraping_data": scraping_data,
        "processing_data": response,
        "status": "success"
    })


def main():
    parser = argparse.ArgumentParser(description="Servidor A - Scraping (IPv4/IPv6)")
    parser.add_argument("--ip", default="::", help="Dirección IP")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--b_ip", default="::1", help="IP del servidor B")
    parser.add_argument("--b_port", type=int, default=9000)

    args = parser.parse_args()

    app = web.Application()
    app["b_host"] = args.b_ip
    app["b_port"] = args.b_port

    app.add_routes([web.get("/scrape", handle_scrape)])

    print(f"[Servidor A] Escuchando en http://[{args.ip}]:{args.port}")
    print(f"[Servidor A] Enviando requests a Servidor B en [{args.b_ip}]:{args.b_port}")

    web.run_app(
    app,
    host=["0.0.0.0", "::"],
    port=args.port
)



if __name__ == "__main__":
    main()
