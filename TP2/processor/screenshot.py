from playwright.sync_api import sync_playwright
import base64
from io import BytesIO

def take_screenshot(url: str) -> str:
    """
    Genera una captura de pantalla real en modo headless usando Playwright
    y devuelve la imagen codificada en base64.
    """
    print(f"[Screenshot] Capturando {url}...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 800})
        try:
            page.goto(url, timeout=15000)  # 15 s máximo
            buffer = page.screenshot(full_page=True)
            browser.close()
            # codificar a base64
            encoded = base64.b64encode(buffer).decode('utf-8')
            return encoded
        except Exception as e:
            print(f"Error al capturar {url}: {e}")
            browser.close()
            return ""
