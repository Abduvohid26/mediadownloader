import asyncio
from playwright.async_api import async_playwright


class BrowserManager:
    def __init__(self, proxy_config=None, interval=600):
        self.proxy_config = proxy_config
        self.interval = interval

        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def init_browser(self, action=None):
        if self.browser is None:
            print("🔄 Brauzer ishga tushirilmoqda...")

            self.playwright = await async_playwright().start()
            options = {
                "headless": True,
                "args": ["--no-sandbox", "--disable-setuid-sandbox"]
            }

            if self.proxy_config:
                options["proxy"] = self.proxy_config

            self.browser = await self.playwright.chromium.launch(**options)
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()

            # Action bo'lsa, sahifaga o'tamiz
            if action == "instagram":
                pass  # Siz bu yerda Instagram sahifasiga o'tishingiz mumkin
            else:
                await self.page.goto("https://sssinstagram.com/ru/story-saver", timeout=10000)
                await self.page.wait_for_load_state("domcontentloaded")

    async def close_browser(self):
        print("❌ Brauzer yopilmoqda...")
        if self.page:
            await self.page.close()
            self.page = None
        if self.context:
            await self.context.close()
            self.context = None
        if self.browser:
            await self.browser.close()
            self.browser = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None

    async def restart_browser(self, action=None):
        await self.close_browser()
        await self.init_browser(action=action)

    async def keep_alive(self, action=None):
        while True:
            await asyncio.sleep(self.interval)
            await self.restart_browser(action=action)
