# client.py
import aiohttp
import asyncio

async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://127.0.0.1:8000/scrape?url=https://example.com') as resp:
            print(await resp.json())

asyncio.run(main())
