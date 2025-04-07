import asyncio
import logging
from urllib.parse import urlparse

from fastapi import APIRouter
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
# from .proxy_route import get_proxy_config
# from .cashe import redis_client
import weakref
# Logger sozlamalari
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class BrowserPool:
    def __init__(self, pool_size=10, proxy_config=None):
        self.pool_size = pool_size
        self.proxy_config = proxy_config
        self.pool = asyncio.Queue()
        self.lock = asyncio.Lock()
        self.playwright = None
        self.initialized = False

    async def initialize(self):
        """Brauzer pool ni ishga tushiradi va 10 ta brauzerni tayyorlaydi"""
        async with self.lock:
            if self.initialized:
                return
            self.initialized = True
            self.playwright = await async_playwright().start()

            tasks = [asyncio.create_task(self._create_browser_instance()) for _ in range(self.pool_size)]
            await asyncio.gather(*tasks)
            logger.info(f"✅ {self.pool_size} ta browser tayyor!")

    async def _create_browser_instance(self):
        """Yangi brauzer yaratib, kerakli sahifani avtomatik ochish"""
        try:
            options = {
                "headless": True,
                "args": [
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",  # Bot sifatida aniqlanishni oldini olish
                    "--disable-infobars",
                    "--no-first-run"
                ],
                "timeout": 60000
            }
            if self.proxy_config:
                options["proxy"] = self.proxy_config

            browser = await self.playwright.chromium.launch(**options)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
                java_script_enabled=True
            )
            
            # Yangi sahifa ochib kerakli URLga o'tamiz
            page = await context.new_page()
            await self._navigate_initial_page(page)
            print(page, "NEW PAGES")
            await self.pool.put((browser, context, page))
            logger.info(f"✅ Browser yaratildi va sahifa tayyor!")

        except Exception as e:
            logger.error(f"❌ Browser yaratishda xato: {e}")
            await self._retry_create_instance()

    async def _navigate_initial_page(self, page, max_retries=3):
        """Kerakli sahifaga borishni ta'minlash"""
        for attempt in range(max_retries):
            try:
                await page.goto("https://sssinstagram.com/ru/story-saver", timeout=20000)
                logger.info("🔍 Sahifa muvaffaqiyatli yuklandi")
                return
                
            except Exception as e:
                logger.warning(f"⚠️ Sahifaga kirishda xato ({attempt+1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(1)
                await page.reload()

    async def release_browser(self, browser_instance):
        """Brauzerni qaytarishda sahifani qayta tiklash"""
        browser, context, page = browser_instance
        try:
            pages = context.pages
            for p in pages[1:]:  
                await p.close()

            await self._navigate_initial_page(page)
            
        except Exception as e:
            logger.error(f"⚠️ Sahifani tiklashda xato: {e}")
            await page.close()
            page = await context.new_page()
            await self._navigate_initial_page(page)
            
        finally:
            await self.pool.put((browser, context, page))

    async def get_browser(self):
        """Pool dan mavjud brauzerni qaytaradi yoki kutib turadi"""
        await self.initialize()
        browser_instance = await self.pool.get()
        return browser_instance


    async def close_all(self):
        """Barcha brauzerlarni yopadi"""
        while not self.pool.empty():
            browser, context, page = await self.pool.get()
            await page.close()
            await context.close()
            await browser.close()

        if self.playwright:
            await self.playwright.stop()
            self.playwright = None


async def get_instagram_story_urls(username, browser_pool):
    """ Instagram storylarini olish """
    try:
        browser_instance = await browser_pool.get_browser()
        if not browser_instance:
            logger.error("❌ Failed to acquire browser")
            return {"error": True, "message": "Browser acquisition failed"}

        browser, context, page = browser_instance

        await page.fill(".form__input", username)
        await page.click(".form__submit")

        await page.wait_for_selector(".button__download", timeout=10000)

        story_links = [await el.get_attribute("href") for el in await page.locator(".button__download").all()]
        print(len(story_links), 'len')
        if not story_links:
            return {"error": True, "message": "Invalid response from the server"}

        return {
            "error": False,
            "hosting": "instagram",
            "type": "stories",
            "username": username,
            "medias": [{"download_url": url, "type": "image" if url.lower().endswith(".jpg") else "video"} for url in story_links]
        }
    except Exception as e:
        return {"error": True, "message": f"Error: {e}"}

# from .proxy_route import get_proxy_config
browser_pool_ref = None

async def init_browser_pool():
    global browser_pool_ref

    if browser_pool_ref is not None:
        browser_pool = browser_pool_ref()
        if browser_pool is not None:
            return browser_pool
    # proxy = await get_proxy_config()
    proxy = {'server': 'http://23.142.16.211:2952', 'username': 'javokhir', 'password': 'mvcs42yr5aj'}
    browser_pool = BrowserPool(pool_size=1, proxy_config=proxy)
    await browser_pool.initialize()

    browser_pool_ref = weakref.ref(browser_pool)
    return browser_pool
# FastAPI marshruti
# checker_router = APIRouter()

# @checker_router.get("/checker/")
# async def checker(url: str):
#     logger.info("Checker endpoint called ✅✅✅✅✅")
#     pool = await init_browser_pool()
#     print(pool, "Poll Exist")
#     data = await get_instagram_story_urls(
#         username=url,
#         browser_pool=pool
#     )
#     logger.info(f"Response data: {data}")
#     return data

async def check_hand(url):
    pool = await init_browser_pool()
    # data = await get_instagram_post_images(post_url=url, caption="salom", browser_pool=pool)
    data = await get_instagram_story_urls(url, pool)
    logger.info(f"Response data: {data}")
    return data

if __name__ == "__main__":
    url = "https://www.instagram.com/p/DHgWbewsTwH/?utm_source=ig_web_copy_link"
    data = asyncio.run(check_hand(url))
    print(data)