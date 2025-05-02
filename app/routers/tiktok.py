import asyncio
from playwright.async_api import async_playwright

async def download_from_snaptik(url, request):
    """Snaptik orqali TikTok videolarini yuklab olish funksiyasi."""

    try:
        page = await asyncio.wait_for(request.app.state.page_pool2.get(), timeout=10)

    except asyncio.TimeoutError:
        return {"error": True, "message": "Server band. Iltimos, keyinroq urinib ko‘ring."}

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
        except Exception as e:
            logger.warning(f"⚠️ Sarlavha topishda xatolik: {e}")

        # Thumbnail (video-header img dan)
        thumb_url = None
        try:
            thumb_img = await page.query_selector(".video-header img")
            if thumb_img:
                thumb_url = await thumb_img.get_attribute("src")
        except Exception as e:
            logger.warning(f"⚠️ Thumbnail topishda xatolik: {e}")

        # Video links (bir nechta bo'lishi mumkin)
        try:
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
        except Exception as e:
            logger.warning(f"⚠️ Video linklar topishda xatolik: {e}")

        # Agar video bo‘lmasa — rasm variantini ko‘rsatamiz
        if not result["medias"]:
            try:
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
            except Exception as e:
                logger.warning(f"⚠️ Rasm topishda xatolik: {e}")

        # Hech qanday media topilmasa
        if not result["medias"]:
            return {"error": True, "message": "Hech qanday media topilmadi."}

        return result

    except Exception as e:
        logger.error(f"❌ Xatolik: {e}")
        return {"error": True, "message": "Serverdan noto‘g‘ri javob oldik."}

    finally:
        # Sahifani tozalab, navbatga qaytarish yoki yopish
        if not page.is_closed():
            try:
                await page.evaluate('document.querySelector("input[name=\'url\']").value = ""')
                await page_pool.put(page)
            except Exception as e:
                logger.warning(f"⚠️ Sahifani qayta navbatga qo‘yishda xatolik: {e}")
                await page.close()