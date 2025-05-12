import asyncio
from playwright.async_api import async_playwright
import logging

logger = logging.getLogger(__name__)


# async def download_from_snaptik(url, request):
#     async with request.app.state.restart_lock:
#         try:
#             page = await asyncio.wait_for(request.app.state.page_pool2.get(), timeout=10)
#         except asyncio.TimeoutError:
#             return {"error": True, "message": "Server band. Iltimos, keyinroq urinib ko‘ring."}

#         try:
#             await page.wait_for_timeout(1000)
#             await page.fill("input[name='vid']", url)
#             try:
#                 await page.wait_for_selector('button:has-text("Consent")', timeout=10000)
#                 await page.click('button:has-text("Consent")')
#                 logger.info("✅ Consent bosildi")
#             except:
#                 logger.warning("❌ Consent oynasi topilmadi")
#             await page.wait_for_selector("button#search-btn", timeout=5000)
#             await page.click("button#search-btn")
#             await page.wait_for_timeout(4000)

#             result = {
#                 "error": False,
#                 "shortcode": None,
#                 "hosting": "tiktok",
#                 "type": None,
#                 "title": None,
#                 "url": url,
#                 "medias": []
#             }

 
#             try:
#                 title_element = await page.query_selector("#tk-search-h2")
#                 if title_element:
#                     result["title"] = (await title_element.inner_text()).strip()
#             except Exception as e:
#                 logger.warning(f"⚠️ Sarlavha topishda xatolik: {e}")
#                 print(f"⚠️ Sarlavha topishda xatolik: {e}")

#             image_links = await page.query_selector_all(".media-box")

#             if not image_links:
#                 try:
#                     video_links = await page.query_selector_all(".tk-down-link")
#                     if len(video_links) >= 2:
#                         a_tag = await video_links[1].query_selector("a")
#                         if a_tag:
#                             href = await a_tag.get_attribute("href")
#                             thumb_img = await page.query_selector("img[alt*='promokod']")
#                             thumb_url = None
#                             if thumb_img:
#                                 thumb_url = await thumb_img.get_attribute("src")
#                             if href:
#                                 result["medias"].append({
#                                     "type": "video",
#                                     "download_url": href,
#                                     "thumb": thumb_url
#                                 })
#                                 result["type"] = "video"
#                 except Exception as e:
#                     logger.warning(f"⚠️ Video linklar topishda xatolik: {e}")
#                     print(f"⚠️ Video linklar topishda xatolik: {e}")
#             else:
#                 try:
#                     for image in image_links:
#                         img_tag = await image.query_selector("img")
#                         if img_tag:
#                             src = await img_tag.get_attribute("src")
#                             if src:
#                                 result["medias"].append({
#                                     "type": "image",
#                                     "download_url": src,
#                                     "thumb": src
#                                 })
#                                 result["type"] = "image"
#                 except Exception as e:
#                     logger.warning(f"⚠️ Rasm topishda xatolik: {e}")
#                     print(f"⚠️ Rasm topishda xatolik: {e}")

#             if not result["medias"]:
#                 return {"error": True, "message": "Hech qanday media topilmadi."}

#             return result

#         except Exception as e:
#             logger.error(f"❌ Xatolik: {e}")
#             return {"error": True, "message": "Serverdan noto‘g‘ri javob oldik."}
#         finally:
#             if not page.is_closed():
#                 try:
#                     await page.reload()
#                     await request.app.state.page_pool2.put(page)
#                 except Exception as e:
#                     logger.warning(f"⚠️ Sahifani qayta navbatga qo‘yishda xatolik: {e}")
#                     await page.close()
import time

async def download_from_snaptik(url, request):
    page = None
    # async with request.app.state.restart_lock:
    click_info = request.app.state.click_info
    print(click_info, "info")

    if click_info is True:
        print({"success": False, "message": "Restart time bro"})
        return await download_from_snaptik_extra(url, request)
        # return {"success": False, "message": "Restart time bro"}

    try:

        page = await asyncio.wait_for(request.app.state.page_pool2.get(), timeout=10)
    except asyncio.TimeoutError:
        return {"error": True, "message": "Server band. Iltimos, keyinroq urinib ko‘ring."}

    try:
        # try:
        consent = await page.query_selector('button:has-text("Consent")')
        if consent:
            await page.click('button:has-text("Consent")')
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
            video_links_divs = await page.query_selector(".video-links")
            # for div in video_links_divs:
            a_tag = await video_links_divs.query_selector("a")
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
            print("salom")
            try:
                back = await page.query_selector(".is-black")
                if back:
                    await back.click()
                else:
                    await page.goto("https://snaptik.app")
                await request.app.state.page_pool2.put(page)
            except Exception as e:
                logger.warning(f"⚠️ Sahifani qayta navbatga qo‘yishda xatolik: {e}")
                await page.close()



async def download_from_snaptik_extra(url, request):
    """Snaptik orqali TikTok videolarini yuklab olish funksiyasi."""
    page = None

    try:
        context = request.app.state.extra_context
        page = await context.new_page()
        await page.goto("https://snaptik.app", wait_until="load", timeout=7000)
    except Exception as e:
        print(f"Xatolik yuzb berdi: {e}")
        return {"error": True, "message": "Error response from the server."}

    try:
        # try:
        consent = await page.query_selector('button:has-text("Consent")')
        if consent:
            await page.click('button:has-text("Consent")')
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
            video_links_divs = await page.query_selector(".video-links")
            # for div in video_links_divs:
            a_tag = await video_links_divs.query_selector("a")
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
        if page:
            await page.close()