import aiohttp
import asyncio

fetch_api = "http://localhost:8000/tiktok/media/service/"

# video_urls = [
#     f"https://www.tiktok.com/@user/video/{1000000000 + i}"
#     for i in range(15)
# ]

url = "https://vt.tiktok.com/ZShbaVon2/"

async def fetch(session, idx, url):
    try:
        async with session.post(fetch_api, data={"url": url}) as response:
            data = await response.text()
            return idx, response.status, data
    except Exception as e:
        return idx, "Error", str(e)

# 2. Asosiy funksiya
async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch(session, i + 1, url) for i in range(4)
        ]

        for coro in asyncio.as_completed(tasks):
            idx, status, data = await coro
            print(f"\n🔹 Request #{idx} -> Status: {status}")
            print(f"📦 Response: {data}...")  # faqat 300 ta belgigacha

# 3. Ishga tushirish
if __name__ == "__main__":
    asyncio.run(main())
