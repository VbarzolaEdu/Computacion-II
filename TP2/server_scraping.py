import asyncio
import argparse
from aiohttp import web, ClientError
from scraper.html_parser import parse_html
from scraper.async_http import fetch_html
from common.protocol import safe_socket_request, log_error


async def handle_scrape(request):
    url = request.query.get('url')
    if not url:
        return web.json_response({"error": "missing_url"}, status=400)

    try:
        html = await fetch_html(url)
        data = parse_html(html)
        processing = await asyncio.to_thread(safe_socket_request, {"url": url})

        return web.json_response({
            "url": url,
            "scraping_data": data,
            "processing_data": processing,
            "status": "success"
        })

    except asyncio.TimeoutError:
        log_error(f"Timeout al scrapear {url}")
        return web.json_response({"error": "timeout_fetching_url"}, status=504)
    except ClientError as e:
        log_error(f"Error de cliente HTTP: {e}")
        return web.json_response({"error": "client_error"}, status=502)
    except Exception as e:
        log_error(f"Error inesperado en servidor A: {e}")
        return web.json_response({"error": str(e)}, status=500)


def main():
    # --- CLI ARGPARSE ---
    parser = argparse.ArgumentParser(
        description="Servidor de Scraping Web Asíncrono"
    )
    parser.add_argument('-i', '--ip', required=True, help='Dirección de escucha (IPv4 o IPv6)')
    parser.add_argument('-p', '--port', required=True, type=int, help='Puerto de escucha')
    parser.add_argument('-w', '--workers', type=int, default=4, help='Número de workers (default: 4)')
    args = parser.parse_args()

    # --- ARRANQUE DEL SERVIDOR ---
    app = web.Application()
    app.router.add_get('/scrape', handle_scrape)

    print(f"🌐 Servidor A escuchando en {args.ip}:{args.port} con {args.workers} workers")
    web.run_app(app, host=args.ip, port=args.port)


if __name__ == '__main__':
    main()
