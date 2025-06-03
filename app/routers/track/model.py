import aiohttp
from shazamio import Shazam




class ShazamWrapper:
    def __init__(self):
        self.shazam = Shazam()
        self.session = None
    async def setup(self, proxy):
        timeout = aiohttp.ClientTimeout(total=20)
        connector = aiohttp.TCPConnector(ssl=False, limit=10)
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            proxy=proxy
        )
        self.shazam.session = self.session

    async def close(self):
        if self.session:
            await self.session.close()

    async def recognize(self, file_path):
        return await self.shazam.recognize(file_path)
    




