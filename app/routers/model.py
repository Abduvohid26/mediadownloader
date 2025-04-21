import asyncio
from playwright.async_api import async_playwright
from .proxy_route import get_proxy_config

class BrowserManager:
    def __init__(self, interval):
        self.proxy_config = None
        self.interval = interval

        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.page_in = None

    async def init_browser(self):
        if self.browser is None:
            self.proxy_config = await get_proxy_config()
            print("🔄 Brauzer ishga tushirilmoqda...", self.proxy_config, "Proxy")

            self.playwright = await async_playwright().start()
            options = {
                "headless": True,
                "args": ["--no-sandbox", "--disable-setuid-sandbox"]
            }
            if self.proxy_config:
                options["proxy"] = {
                    "server": f"http://{self.proxy_config['server'].replace('http://', '')}",
                    "username": self.proxy_config['username'],
                    "password": self.proxy_config['password']
                }
            self.browser = await self.playwright.chromium.launch(**options)
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()
            self.page_in = await self.context.new_page()

            await self.page.goto("https://sssinstagram.com/ru/story-saver", timeout=10000)
            await self.page_in.goto("https://www.instagram.com", timeout=30000)
            await self.page_in.wait_for_load_state("domcontentloaded")

            print(f"🔄 Instagram va Ssinstagram sahifasi tayyor: \n{self.proxy_config}")    

    async def goto_reel(self, url):
        if not self.page_in:
            raise Exception("Brauzer hali ishga tushmagan")
        
        # URL oxirini ajratamiz
        path = url.replace("https://www.instagram.com/", "")
        full_url = f"https://www.instagram.com/{path}"
        print(f"➡️ O'tilmoqda: {full_url}")
        await self.page_in.goto(full_url, timeout=30000)
        # await self.page_in.wait_for_selector("article", timeout=15000)
        print("✅ Reels sahifa yuklandi!")


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
        if self.page_in:
            await self.page_in.close()
            self.page_in = None

    async def restart_browser(self, action=None):
        await self.close_browser()
        await self.init_browser(action=action)

    async def keep_alive(self, action=None):
        while True:
            await asyncio.sleep(self.interval)
            await self.restart_browser(action=action)
