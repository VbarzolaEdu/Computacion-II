# server_scraping.py
import asyncio
from aiohttp import web
from scraper.html_parser import parse_html
from scraper.async_http import fetch_html
import json
import socket


import asyncio
import socket
import json

async def request_processing(url: str):
    """
    Envía una URL al servidor de procesamiento (Parte B)
    y devuelve los resultados.
    """
    data = json.dumps({'url': url}).encode()

    def communicate():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("127.0.0.1", 9000))
            s.sendall(data)
            response = s.recv(65536)
            return json.loads(response)

    # Ejecutar comunicación sin bloquear el event loop
    return await asyncio.to_thread(communicate)



async def handle_scrape(request):
    url = request.query.get('url')
    if not url:
        return web.json_response({'error': 'missing URL'}, status=400)

    html = await fetch_html(url)
    data = parse_html(html)


    processing = await request_processing(url)
    return web.json_response({
        'url': url,
        'scraping_data': data,
        'processing_data': processing,
        'status': 'success'
    })




def main():
    app = web.Application()
    app.router.add_get('/scrape', handle_scrape)
    web.run_app(app, host='127.0.0.1', port=8000)

if __name__ == '__main__':
    main()
