# client.py
import aiohttp
import asyncio
import json

async def main():
    url = input("Ingrese la URL a scrapear: ").strip()

    api_url = f"http://127.0.0.1:8000/scrape?url={url}"

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as resp:
            data = await resp.json()
            print(json.dumps(data, indent=4))

asyncio.run(main())
