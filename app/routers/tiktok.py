import asyncio
from playwright.async_api import async_playwright

async def download_from_snaptik(url, request):
    page_pool = request.app.state.page_pool2
    page = await page_pool.get()

    try:
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
            title_element = await page.query_selector(".video-title")
            if title_element:
                result["title"] = (await title_element.inner_text()).strip()
        except:
            pass

        # ✅ Faqat bitta thumb olish — image joyidan (video-header)
        thumb_url = None
        try:
            thumb_img = await page.query_selector(".video-header img")
            if thumb_img:
                thumb_url = await thumb_img.get_attribute("src")
        except:
            pass

        # Video links — thumb hamisha image joyidan
        video_links_divs = await page.query_selector_all(".video-links")
        for div in video_links_divs:
            a_tag = await div.query_selector("a")
            if a_tag:
                href = await a_tag.get_attribute("href")
                if href:
                    result["medias"].append({
                        "type": "video",
                        "download_url": href,
                        "thumb": thumb_url
                    })
                    result["type"] = "video"

        # Agar video topilmasa — image bo'lishi mumkin
        if not result["medias"]:
            image_container = await page.query_selector(".video-header")
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
                result["type"] = "image"

        if not result["medias"]:
            return {"error": True, "message": "Hech qanday media topilmadi."}

        return result

    except Exception as e:
        print("❌ Xatolik:", e)
        return {"error": True, "message": "Serverdan noto‘g‘ri javob oldik."}

    finally:
        if not page.is_closed():
            # error_message = await page.query_selector('.error-message')

            # if error_message:
            #     print("⚠️ Error message topildi, sahifa yopilyapti...")
            #     await page.close()
            # else:
            # await page.evaluate('document.querySelector(".form__input").value = ""')
            await page.reload()
            await page_pool.put(page)