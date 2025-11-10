import requests
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup

def analyze_performance(url: str) -> dict:
    """
    Mide tiempo de carga y tamaño total aproximado de los recursos
    principales (HTML + imágenes + CSS).
    """
    print(f"[Performance] Analizando {url}...")
    start = time.time()
    try:
        resp = requests.get(url, timeout=10)
        html_size = len(resp.content)

        soup = BeautifulSoup(resp.text, 'lxml')
        resource_urls = []
        for tag, attr in [('img', 'src'), ('link', 'href'), ('script', 'src')]:
            for r in soup.find_all(tag):
                link = r.get(attr)
                if link:
                    resource_urls.append(urljoin(url, link))

        total_size = html_size
        count = 0
        for rurl in resource_urls[:15]:  # limitar a 15 recursos
            try:
                r = requests.head(rurl, timeout=5)
                size = int(r.headers.get('Content-Length', 0))
                total_size += size
                count += 1
            except:
                continue

        load_time = int((time.time() - start) * 1000)
        return {
            "load_time_ms": load_time,
            "total_size_kb": round(total_size / 1024, 2),
            "num_requests": count + 1  # +1 por el HTML
        }
    except Exception as e:
        print(f"Error en analyze_performance: {e}")
        return {"load_time_ms": 0, "total_size_kb": 0, "num_requests": 0}
