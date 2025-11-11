import pytest
from scraper.html_parser import parse_html
from scraper.async_http import fetch_html
import asyncio

# --- Test del parser HTML local ---
def test_parse_html_basic():
    html = """
    <html>
      <head>
        <title>Test Page</title>
        <meta name="description" content="A test page">
        <meta property="og:title" content="OG Test Title">
      </head>
      <body>
        <h1>Header</h1>
        <h2>Subheader</h2>
        <img src="img1.png"/>
        <a href="https://example.com">Link</a>
      </body>
    </html>
    """
    data = parse_html(html)

    assert data["title"] == "Test Page"
    assert data["meta_tags"]["description"] == "A test page"
    assert data["structure"]["h1"] == 1
    assert data["images_count"] == 1
    assert "https://example.com" in data["links"]


# --- Test del fetch HTML asíncrono real ---
@pytest.mark.asyncio
async def test_fetch_html():
    # Se usa una URL liviana de ejemplo
    html = await fetch_html("https://example.com")
    assert "<title>Example Domain" in html
