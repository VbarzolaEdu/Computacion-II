import requests
from PIL import Image
from io import BytesIO
import base64
from bs4 import BeautifulSoup

def process_images(url: str) -> list:
    """
    Descarga las primeras imágenes de la página y crea miniaturas en base64.
    """
    print(f"[ImageProc] Procesando imágenes de {url}...")
    try:
        html = requests.get(url, timeout=10).text
        soup = BeautifulSoup(html, 'lxml')
        imgs = [img['src'] for img in soup.find_all('img', src=True)][:3]

        thumbs = []
        for src in imgs:
            full_url = src if src.startswith('http') else url + src
            try:
                r = requests.get(full_url, timeout=10)
                img = Image.open(BytesIO(r.content))
                img.thumbnail((150, 150))
                buf = BytesIO()
                img.save(buf, format='PNG')
                encoded = base64.b64encode(buf.getvalue()).decode('utf-8')
                thumbs.append(encoded)
            except Exception as e:
                print(f"   Error con {src}: {e}")
                continue

        return thumbs
    except Exception as e:
        print(f"Error general en process_images: {e}")
        return []
