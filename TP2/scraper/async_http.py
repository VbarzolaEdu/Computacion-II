import aiohttp

async def fetch_html(url: str) -> str:
    """
    Descarga el HTML de una página web de forma asíncrona.
    """
    timeout = aiohttp.ClientTimeout(total=30)  # máximo 30s
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as response:
            return await response.text()
