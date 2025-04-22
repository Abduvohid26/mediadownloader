import asyncio
from playwright.async_api import async_playwright

async def download_from_snaptik(url, context):
    # async with async_playwright() as p:
        # browser = await p.chromium.launch(headless=True)
        # context = await browser.new_context()
        page = await context.new_page()


        try:
            await page.goto("https://snaptik.app", timeout=15000)
            await page.wait_for_timeout(1000)
            await page.mouse.click(10, 10)
            await page.fill("input[name='url']", url)
            await page.click("button[type='submit'][aria-label='Get']")
            await page.wait_for_timeout(4000)

            result = {
                "error": False,
                "shortcode": None,
                "hosting": "tiktok",
                "type": None,
                "url": url,
                "title": None,
                "medias": []
            }

            # Title
            try:
                title_element = await page.query_selector("div.is-size-5")
                if title_element:
                    result["title"] = (await title_element.inner_text()).strip()
            except:
                pass

            # Thumbnail olish
            thumb_url = None
            try:
                thumb = await page.query_selector(".columns .column img")
                if thumb:
                    thumb_url = await thumb.get_attribute("src")
            except:
                pass

            # Video links
            video_links_divs = await page.query_selector_all(".video-links")
            for div in video_links_divs:
                a_tag = await div.query_selector("a")
                if a_tag:
                    href = await a_tag.get_attribute("href")
                    if href:
                        result["medias"].append({
                            "type": "video",
                            "download_url": href,
                            "thumb": thumb_url  # Faqat shu yerda
                        })
                        result["type"] = "video"

            # Image links
            image_container = await page.query_selector(".is-multiline")
            if image_container:
                img_tags = await image_container.query_selector_all("img")
                for img in img_tags:
                    src = await img.get_attribute("src")
                    if src:
                        result["medias"].append({
                            "type": "image",
                            "download_url": src,
                            "thumb": src
                        })
                        result["type"] = result["type"] or "image"

            if not result["medias"]:
                print("❌ Hech qanday media topilmadi.")
                return None

            return result

        except Exception as e:
            print("❌ Xatolik:", e)
            return None