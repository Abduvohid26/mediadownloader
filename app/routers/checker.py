
from playwright.async_api import async_playwright
import asyncio
import re

# async def get_instagram_story_urls(username: str, context):
#     """Instagram hikoyalarini yuklab olish funksiyasi."""
#     try:
#         page = await context.new_page()

#         # Saytga kirish
#         await page.goto("https://sssinstagram.com/ru/story-saver")

#         # Inputga username qo'yish
#         await page.fill(".form__input", username)
#         await page.click(".form__submit")

#         # Yuklab olish tugmasi chiqquncha kutish
#         await page.wait_for_selector(".button__download", state="attached", timeout=25000)

#         # Storylar uchun yuklab olish linklari
#         story_elements = await page.locator(".button__download").all()
#         story_links = [await el.get_attribute("href") for el in story_elements if await el.get_attribute("href")]

#         # Har bir media uchun thumbnail (prevyu rasm)
#         thumbnail_elements = await page.locator(".media-content__image").all()
#         thumbnails = [await el.get_attribute("src") for el in thumbnail_elements if await el.get_attribute("src")]

#         # Sarlavha olish
#         title_elements = await page.locator(".output-list__caption p").all()
#         titles = [await el.text_content() for el in title_elements]
#         title = titles[0] if titles else None

#         # Shortcode ajratish (ixtiyoriy, agar URLdan topilsa)
#         match = re.search(r'/p/([^/]+)/', username)
#         shortcode = match.group(1) if match else "unknown"

#         if not story_links:
#             return {"error": True, "message": "Hech qanday media topilmadi."}

#         # Media turini aniqlash
#         def detect_type(url: str):
#             return "image" if url.lower().endswith(".jpg") else "video"

#         # Media elementlarini to'plash (thumbnail bilan)
#         medias = []
#         for idx, url in enumerate(story_links):
#             medias.append({
#                 "download_url": url,
#                 "type": detect_type(url),
#                 "thumbnail": thumbnails[idx] if idx < len(thumbnails) else None
#             })

#         return {
#             "error": False,
#             "shortcode": shortcode,
#             "hosting": "instagram",
#             "type": "album" if len(story_links) > 1 else detect_type(story_links[0]),
#             "url": username,
#             "title": title,
#             "medias": medias,
#         }

#     except Exception as e:
#         print(f"Xatolik yuz berdi: {e}")
#         return {"error": True, "message": "Serverdan noto‘g‘ri javob oldik."}

# async def get_instagram_image_and_album_and_reels(post_url, context):
#     print("📥 Media yuklanmoqda...")
#     try:
#         page = await context.new_page()
#         await page.goto(post_url)

#         try:
#             await page.wait_for_selector("article", timeout=20000)
#         except Exception as e:
#             print(f"❌ 'section' elementi topilmadi: {e}")
#             return {"error": True, "message": "Invalid response from the server"}

#         await page.mouse.click(10, 10)
#         await page.wait_for_timeout(1500)

#         caption = None
#         if (caption_el := await page.query_selector('article span._ap3a')):
#             caption = await caption_el.inner_text()

#         media_list = []

#         while True:
#             # 1. RASMLAR faqat article section ichidan olinadi
#             images = await page.locator("article ._aagv img").all()
#             for img in images:
#                 src = await img.get_attribute("src")
#                 if src and not any(m["download_url"] == src for m in media_list):
#                     media_list.append({
#                         "type": "image",
#                         "download_url": src,
#                         "thumb": src
#                     })

#             # 2. VIDEOLAR faqat article section ichidan olinadi
#             videos = await page.locator("article video").all()
#             for video in videos:
#                 src = await video.get_attribute("src")
#                 poster = await video.get_attribute("poster")
#                 if src and not any(m["download_url"] == src for m in media_list):
#                     media_list.append({
#                         "type": "video",
#                         "download_url": src,
#                         "thumbnail": poster or src  # fallback
#                     })

#             # 3. Keyingi media (album ichidagi)
#             try:
#                 next_btn = page.locator("button[aria-label='Next']")
#                 await next_btn.wait_for(timeout=1500)
#                 await next_btn.click()
#                 await page.wait_for_timeout(1000)
#             except Exception:
#                 break

#         if not media_list:
#             return {"error": True, "message": "Hech qanday media topilmadi"}

#         # Shortcode ni URL dan olamiz
#         match = re.search(r'/p/([^/]+)/', post_url)
#         shortcode = match.group(1) if match else "unknown"

#         return {
#             "error": False,
#             "shortcode": shortcode,
#             "hosting": "instagram",
#             "type": "album" if len(media_list) > 1 else media_list[0]["type"],
#             "caption": caption,
#             "medias": media_list
#         }

#     except Exception as e:
#         print(f"❗ Umumiy xatolik: {e}")
#         return {"error": True, "message": "Invalid response from the server"}


async def get_instagram_image_and_album_and_reels(post_url, context):
    print("📥 Media yuklanmoqda...")

    try:
        page = await context.new_page()
        await page.goto(post_url, wait_until="domcontentloaded")  # sahifa to'liq yuklanishini kutadi
        print(page, "Page")
        
        # Sahifa yuklanganidan so'ng
        await page.wait_for_selector("article", timeout=5000)

        caption = None
        if (caption_el := await page.query_selector('article span._ap3a')):
            caption = await caption_el.inner_text()

        media_list = []

        # Rasmlar va videolarni olish
        images = await page.locator("article ._aagv img").all()
        for img in images:
            src = await img.get_attribute("src")
            if src and not any(m["download_url"] == src for m in media_list):
                media_list.append({
                    "type": "image",
                    "download_url": src,
                    "thumb": src
                })

        videos = await page.locator("article video").all()
        for video in videos:
            src = await video.get_attribute("src")
            poster = await video.get_attribute("poster")
            if src and not any(m["download_url"] == src for m in media_list):
                media_list.append({
                    "type": "video",
                    "download_url": src,
                    "thumbnail": poster or src
                })

        # Agar album bo'lsa, keyingi sahifaga o'tish
        next_btn = page.locator("button[aria-label='Next']")
        try:
            await next_btn.wait_for(timeout=1500)
            await next_btn.click()
        except Exception:
            pass

        if not media_list:
            return {"error": True, "message": "Hech qanday media topilmadi"}

        match = re.search(r'/p/([^/]+)/', post_url)
        shortcode = match.group(1) if match else "unknown"

        return {
            "error": False,
            "shortcode": shortcode,
            "hosting": "instagram",
            "type": "album" if len(media_list) > 1 else media_list[0]["type"],
            "caption": caption,
            "medias": media_list
        }

    except Exception as e:
        print(f"❗ Umumiy xatolik: {e}")
        return {"error": True, "message": "Invalid response from the server"}

async def check_itorya():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False, args=["--no-sandbox", "--disable-setuid-sandbox"])
        context = await browser.new_context()
        result = await get_instagram_image_and_album_and_reels("https://www.instagram.com/p/DHgWbewsTwH/?utm_source=ig_web_copy_link", context)
        print(result)
        await browser.close()

# import time
# if __name__ == "__main__":

#     curr_time = time.time() 
#     asyncio.run(check_itorya())
#     print("time", time.time() - curr_time)
# async def get_instagram_story_urls(username: str, context):
#     """Instagram hikoyalarini yuklab olish funksiyasi."""
#     async with async_playwright() as playwright:
#         # proxy = await get_proxy_config()
#         options = {
#             "headless": True,
#             "args": "--no-sandbox --disable-setuid-sandbox"
#         }
#         # if proxy:
#         #     options["proxy"] = {
#         #         "server": f"http://{proxy['server'].replace('http://', '')}",
#         #         "username": proxy['username'],
#         #         "password": proxy['password']
#         #     }
#
#         browser = await playwright.chromium.launch()
#         page = await browser.new_page()
#     try:
#         # page = await context.new_page()
#         # print(page, "PAGE")
#
#         # Saytga kirish
#         await page.goto("https://sssinstagram.com/ru/story-saver")
#
#         # Inputga username qo'yish
#         await page.fill(".form__input", username)
#         await page.click(".form__submit")
#
#         # Yuklab olish tugmasi chiqquncha kutish
#         await page.wait_for_selector(".button__download", state="attached", timeout=25000)
#
#         # Storylar uchun yuklab olish linklari
#         story_elements = await page.locator(".button__download").all()
#         story_links = [await el.get_attribute("href") for el in story_elements if await el.get_attribute("href")]
#
#         # Har bir media uchun thumbnail (prevyu rasm)
#         thumbnail_elements = await page.locator(".media-content__image").all()
#         thumbnails = [await el.get_attribute("src") for el in thumbnail_elements if await el.get_attribute("src")]
#
#         # Sarlavha olish
#         title_elements = await page.locator(".output-list__caption p").all()
#         titles = [await el.text_content() for el in title_elements]
#         title = titles[0] if titles else None
#
#         # Shortcode ajratish (ixtiyoriy, agar URLdan topilsa)
#         match = re.search(r'/p/([^/]+)/', username)
#         shortcode = match.group(1) if match else "unknown"
#
#         if not story_links:
#             return {"error": True, "message": "Hech qanday media topilmadi."}
#
#         # Media turini aniqlash
#         def detect_type(url: str):
#             return "image" if url.lower().endswith(".jpg") else "video"
#
#         # Media elementlarini to'plash (thumbnail bilan)
#         medias = []
#         for idx, url in enumerate(story_links):
#             medias.append({
#                 "type": detect_type(url),
#                 "download_url": url,
#                 "thumbnail": thumbnails[idx] if idx < len(thumbnails) else None
#             })
#
#         return {
#             "error": False,
#             "shortcode": shortcode,
#             "hosting": "instagram",
#             "type": "album" if len(story_links) > 1 else detect_type(story_links[0]),
#             "url": username,
#             "title": title,
#             "medias": medias,
#         }
#
#     except Exception as e:
#         print(f"Xatolik yuz berdi: {e}")
#         return {"error": True, "message": "Serverdan noto‘g‘ri javob oldik."}
#
#     finally:
#         await browser.close()
#
# if __name__ == "__main__":
#     asyncio.run(get_instagram_story_urls())


# async def get_instagram_story_urls(username: str):
#     """Instagram hikoyalarini yuklab olish funksiyasi."""
#     async with async_playwright() as playwright:
#         # proxy = await get_proxy_config()
#         options = {
#             "headless": False,
#             "args": ["--no-sandbox", "--disable-setuid-sandbox"]
#         }
#         # if proxy:
#         #     options["proxy"] = {
#         #         "server": f"http://{proxy['server'].replace('http://', '')}",
#         #         "username": proxy['username'],
#         #         "password": proxy['password']
#         #     }
#
#         browser = await playwright.chromium.launch(**options)
#         page = await browser.new_page()
#         try:
#             # page = await context.new_page()
#             # print(page, "PAGE")
#
#             # Saytga kirish
#             await page.goto("https://sssinstagram.com/ru/story-saver")
#             print(page, "page")
#             # Inputga username qo'yish
#             await page.fill(".form__input", username)
#             await page.click(".form__submit")
#
#             # Yuklab olish tugmasi chiqquncha kutish
#             await page.wait_for_selector(".button__download", timeout=25000)
#
#             # Storylar uchun yuklab olish linklari
#             story_elements = await page.locator(".button__download").all()
#             story_links = [await el.get_attribute("href") for el in story_elements if await el.get_attribute("href")]
#
#             # Har bir media uchun thumbnail (prevyu rasm)
#             thumbnail_elements = await page.locator(".media-content__image").all()
#             thumbnails = [await el.get_attribute("src") for el in thumbnail_elements if await el.get_attribute("src")]
#
#             # Sarlavha olish
#             title_elements = await page.locator(".output-list__caption p").all()
#             titles = [await el.text_content() for el in title_elements]
#             title = titles[0] if titles else None
#
#             # Shortcode ajratish (ixtiyoriy, agar URLdan topilsa)
#             match = re.search(r'/p/([^/]+)/', username)
#             shortcode = match.group(1) if match else "unknown"
#
#             if not story_links:
#                 return {"error": True, "message": "Hech qanday media topilmadi."}
#
#             # Media turini aniqlash
#             def detect_type(url: str):
#                 return "image" if url.lower().endswith(".jpg") else "video"
#
#             # Media elementlarini to'plash (thumbnail bilan)
#             medias = []
#             for idx, url in enumerate(story_links):
#                 medias.append({
#                     "type": detect_type(url),
#                     "download_url": url,
#                     "thumbnail": thumbnails[idx] if idx < len(thumbnails) else None
#                 })
#
#             return {
#                 "error": False,
#                 "shortcode": shortcode,
#                 "hosting": "instagram",
#                 "type": "album" if len(story_links) > 1 else detect_type(story_links[0]),
#                 "url": username,
#                 "title": title,
#                 "medias": medias,
#             }
#
#         except Exception as e:
#             print(f"Xatolik yuz berdi: {e}")
#             return {"error": True, "message": "Serverdan noto‘g‘ri javob oldik."}
#
#         finally:
#             await browser.close()
#
#
# if __name__ == '__main__':
#     asyncio.run(get_instagram_story_urls(username="https://www.instagram.com/stories/khakimov_042/"))

# from playwright.sync_api import sync_playwright
# import json
# import re

# def get_instagram_media(post_url):
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=False)  # headless rejimida
#         page = browser.new_page()
        
#         page.goto(post_url, wait_until="domcontentloaded")  # Sahifa to'liq yuklanguncha kutish
#         page.wait_for_selector('script:has-text("window._sharedData")')  # 'window._sharedData' elementini kutish

#         # Sahifa yuklanganidan so'ng, kerakli skriptni olish
#         script_tag = page.query_selector('script:has-text("window._sharedData")').inner_text()
#         print(script_tag)

#         # Skriptni parsing qilish
#         json_str = re.search(r"window\._sharedData = (.*);", script_tag).group(1)
#         data = json.loads(json_str)

#         media = data["entry_data"]["PostPage"][0]["graphql"]["shortcode_media"]
#         print(f"\n📎 URL: {post_url}")

#         if media.get("edge_sidecar_to_children"):
#             edges = media["edge_sidecar_to_children"]["edges"]
#             for i, edge in enumerate(edges):
#                 node = edge["node"]
#                 if node["is_video"]:
#                     print(f"  🎥 Video {i + 1}: {node['video_url']}")
#                 else:
#                     print(f"  🖼️ Image {i + 1}: {node['display_url']}")
#         else:
#             if media["is_video"]:
#                 print(f"  🎥 Video: {media['video_url']}")
#             else:
#                 print(f"  🖼️ Image: {media['display_url']}")

#         browser.close()

# # Test qilish


# # Test qilish
# get_instagram_media("https://www.instagram.com/p/DIVG5civ8zK/?utm_source=ig_web_copy_link")
