import asyncio
from aiohttp import web, ClientError
from scraper.html_parser import parse_html
from scraper.async_http import fetch_html
from common.protocol import safe_socket_request, log_error

# --- Endpoint principal ---
async def handle_scrape(request):
    url = request.query.get('url')
    if not url:
        return web.json_response({"error": "missing_url"}, status=400)

    try:
        html = await fetch_html(url)
        data = parse_html(html)

        # Comunicación con servidor B (con manejo interno de errores)
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
    app = web.Application()
    app.router.add_get('/scrape', handle_scrape)
    web.run_app(app, host='127.0.0.1', port=8000)


if __name__ == '__main__':
    main()
