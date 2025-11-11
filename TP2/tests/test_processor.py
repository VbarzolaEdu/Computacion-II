import pytest
from processor.performance import analyze_performance
from processor.image_processor import process_images
from processor.screenshot import take_screenshot
import base64

def test_analyze_performance_structure():
    result = analyze_performance("https://example.com")
    assert "load_time_ms" in result
    assert "total_size_kb" in result
    assert "num_requests" in result
    assert isinstance(result["load_time_ms"], int)


def test_process_images_returns_list():
    thumbs = process_images("https://example.com")
    assert isinstance(thumbs, list)
    # Puede ser vacío si no hay imágenes, pero no debe romperse


def test_take_screenshot_returns_base64():
    img_data = take_screenshot("https://example.com")
    # Si Playwright no puede abrir, devolverá string vacío, pero no debe romper
    assert isinstance(img_data, str)
    if img_data:
        # Validar formato base64 mínimo
        try:
            base64.b64decode(img_data)
        except Exception:
            pytest.fail("Screenshot no está en base64 válido")
