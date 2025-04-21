import asyncio
from playwright.async_api import async_playwright

async def download_from_snaptik(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            await page.goto("https://snaptik.app", timeout=15000)
            await page.wait_for_timeout(1000)
            await page.mouse.click(10, 10)  # Ekranning chap yuqori burchagiga klik
            await page.fill("input[name='url']", url)
            await page.click("button[type='submit'][aria-label='Get']")
            await page.wait_for_timeout(4000)

            result = {
                "error": False,
                "url": url,
                "type": None,
                "hosting": "tiktok",
                "medias": []
            }

            # Video linklarni olish
            video_links_divs = await page.query_selector_all(".video-links")
            for div in video_links_divs:
                a_tag = await div.query_selector("a")
                if a_tag:
                    href = await a_tag.get_attribute("href")
                    if href:
                        result["medias"].append({
                            "download_url": href,
                            "type": "video"
                        })
                        result["type"] = "video"

            # Rasm (image) linklarni olish
            image_container = await page.query_selector(".is-multiline")
            if image_container:
                img_tags = await image_container.query_selector_all("img")
                for img in img_tags:
                    src = await img.get_attribute("src")
                    if src:
                        result["medias"].append({
                            "download_url": src,
                            "type": "image"
                        })
                        if not result["type"]:
                            result["type"] = "image"

            if not result["medias"]:
                print("❌ Hech qanday media topilmadi. Sayt bloklagan bo'lishi mumkin.")
                return None

            return result

        except Exception as e:
            print("❌ Xatolik:", e)
            return None

        finally:
            await browser.close()