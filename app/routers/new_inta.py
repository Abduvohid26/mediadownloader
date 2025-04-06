import asyncio
import logging
from urllib.parse import urlparse

from fastapi import APIRouter
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from .proxy_route import get_proxy_config
from .cashe import redis_client
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
        """Yangi brauzer yaratadi va uni pool ga qo'shadi"""
        try:
            options = {
                "headless": True,
                "args": ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage", "--single-process"],
                "timeout": 60000
            }
            if self.proxy_config:
                options["proxy"] = self.proxy_config

            browser = await self.playwright.chromium.launch(**options)
            context = await browser.new_context()
            page = await context.new_page()

            try:
                await page.goto("https://sssinstagram.com/ru/story-saver", timeout=20000)
                await page.wait_for_load_state("domcontentloaded")
            except Exception as e:
                logger.warning(f"⚠️ Initial page load failed: {e}")
                await page.close()
                page = await context.new_page()

            await self.pool.put((browser, context, page))
        except Exception as e:
            logger.error(f"❌ Error creating browser instance: {e}")

    async def get_browser(self):
        """Pool dan mavjud brauzerni qaytaradi yoki kutib turadi"""
        await self.initialize()
        browser_instance = await self.pool.get()
        return browser_instance

    async def release_browser(self, browser_instance):
        """Brauzerni qayta ishlashga tayyorlab pool ga qaytaradi"""
        browser, context, page = browser_instance
        try:
            await page.goto("https://sssinstagram.com/ru/story-saver")
            await page.wait_for_load_state("domcontentloaded")
        except Exception as e:
            logger.warning(f"⚠️ Error resetting page: {e}")
            await page.close()
            page = await context.new_page()

        await self.pool.put((browser, context, page))

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

async def get_instagram_post_images(post_url, caption, browser_pool):
    """Instagram postdan rasmlar olish funksiyasi"""
    try:
        browser_instance = await browser_pool.get_browser()
        if not browser_instance:
            logger.error("❌ Failed to acquire browser")
            return {"error": True, "message": "Browser acquisition failed"}

        browser, context, page = browser_instance

        # try:
        #     await page.goto(post_url, timeout=15000)
        # except PlaywrightTimeoutError:
        #     logger.error("❌ Timeout loading the page")
        #     await browser_pool.release_browser(browser_instance)
        #     return {"error": True, "message": "Timeout loading page"}

        path = urlparse(post_url).path
        shortcode = path.strip("/").split("/")[-1]

        try:
            await page.wait_for_selector("article", timeout=15000)
        except PlaywrightTimeoutError:
            logger.error("❌ 'article' element not found")
            await browser_pool.release_browser(browser_instance)
            return {"error": True, "message": "Post content not found"}

        image_urls = set()
        await page.mouse.click(10, 10)
        await asyncio.sleep(0.5)

        while True:
            images = await page.locator("article ._aagv img").all()
            for img in images:
                url = await img.get_attribute("src")
                if url:
                    image_urls.add(url)

            next_button = page.locator("button[aria-label='Next']")
            if await next_button.count() > 0:
                prev_count = len(image_urls)
                await next_button.click()
                await asyncio.sleep(0.5)
                if len(image_urls) == prev_count:
                    break
            else:
                break

        if not image_urls:
            logger.error("❌ No image URLs found")
            await browser_pool.release_browser(browser_instance)
            return {"error": True, "message": "No images found"}

        await browser_pool.release_browser(browser_instance)
        return {
            "error": False,
            "hosting": "instagram",
            "type": "album" if len(image_urls) > 1 else "image",
            "shortcode": shortcode,
            "caption": caption,
            "medias": [{"type": "image", "download_url": url, "thumb": url} for url in image_urls]
        }
    except Exception as e:
        logger.error(f"❌ Unknown error: {str(e)}")
        return {"error": True, "message": "Internal server error"}


browser_pool_ref = None

async def init_browser_pool():
    global browser_pool_ref

    if browser_pool_ref is not None:
        browser_pool = browser_pool_ref()
        if browser_pool is not None:
            return browser_pool

    proxy = await get_proxy_config()
    browser_pool = BrowserPool(pool_size=10, proxy_config=proxy)
    await browser_pool.initialize()

    browser_pool_ref = weakref.ref(browser_pool)
    return browser_pool
# FastAPI marshruti
checker_router = APIRouter()

@checker_router.get("/checker/")
async def checker(url: str):
    logger.info("Checker endpoint called ✅✅✅✅✅")
    print("Checker endpoint called ✅✅✅✅✅")
    pool = await init_browser_pool()
    print(pool, "Pool")
    data = await get_instagram_post_images(
        post_url=url,
        caption="salom",
        browser_pool=pool
    )
    logger.info(f"Response data: {data}")
    return data