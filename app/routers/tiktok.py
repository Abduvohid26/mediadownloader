# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.keys import Keys
# from webdriver_manager.chrome import ChromeDriverManager
# import time
from enum import unique

# def get_tiktok_download_url(video_url):
#     options = webdriver.ChromeOptions()
#     #options.add_argument("--headless")  # Brauzerni yashirin rejimda ochish
#     options.add_argument("--disable-gpu")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")

#     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
#     try:
#         driver.get("https://ssstik.io/en")
#         time.sleep(3)  

#         # TikTok linkini inputga kiritish
#         input_box = driver.find_element(By.NAME, "id")
#         input_box.send_keys(video_url)
#         input_box.send_keys(Keys.RETURN)  

#         time.sleep(5)  # Sayt yuklanishini kutish

#         # Albom rasmlarini o‘z ichiga olgan `ul` topish
#         album_list = driver.find_elements(By.CLASS_NAME, "splide__list")

#         if not album_list:
#             return "Xatolik: Albom rasmlari topilmadi!"

#         # `li` taglari ichidan `a[href]` havolalarini olish
#         image_links = []
#         li_tags = album_list[0].find_elements(By.TAG_NAME, "li")
        
#         for li in li_tags:
#             a_tag = li.find_element(By.TAG_NAME, "a")  # `a` tegini olish
#             image_links.append(a_tag.get_attribute("href"))  # `href`ni olish
        
#         return {"album_link": image_links} if image_links else "Xatolik: Albom rasmlari topilmadi!"

#     except Exception as e:
#         return f"Xatolik yuz berdi: {str(e)}"
    
#     finally:
#         driver.quit()  

    

# # Foydalanish
# tiktok_url = "https://vt.tiktok.com/ZSrLJ2KnQ"
# download_url = get_tiktok_download_url(tiktok_url)
# print("Yuklab olish havolasi:", download_url)


# import yt_dlp

# def download_instagram_image(instagram_url):
#     options = {
#         "skip_download": True,  # Videoni yuklamaslik
#         "writethumbnail": True,  # Faqat rasm yuklash
#         "outtmpl": "%(title)s.%(ext)s"  # Fayl nomini saqlash
#     }

#     with yt_dlp.YoutubeDL(options) as ydl:
#         info = ydl.extract_info(instagram_url, download=True)
#         return info.get("thumbnail")

# # Test
# instagram_post = "https://www.instagram.com/p/DHoPq-KMSgP/?utm_source=ig_web_copy_link"
# image_url = download_instagram_image(instagram_post)
# print("Rasm URL:", image_url)


# import yt_dlp

# def get_instagram_download_link(instagram_url):
#     options = {
#         "skip_download": True,  # Faqat link olish, yuklab olmaslik
#     }

#     with yt_dlp.YoutubeDL(options) as ydl:
#         info = ydl.extract_info(instagram_url, download=False)  # Faqat ma'lumot olish
#         print(info, 'info')
#         return info.get("url")  # To‘g‘ridan-to‘g‘ri yuklab olish linki

# # Test qilish
# instagram_post = "https://www.instagram.com/stories/fargona_tezkor/"
# # instagram_post = "https://www.instagram.com/p/DHoPq-KMSgP/?utm_source=ig_web_copy_link"
# # instagram_post  = "https://www.instagram.com/reel/DE30_MpoUbh/?utm_source=ig_web_copy_link"
# download_link = get_instagram_download_link(instagram_post)

# print("Yuklab olish linki:", download_link)

# import yt_dlp


# def get_instagram_story_url(story_url):
#     options = {
#         "skip_download": True,  # Faqat link olish
#         "cookies": "cookies.txt"  # Cookies faylni yuklash
#     }

#     with yt_dlp.YoutubeDL(options) as ydl:
#         info = ydl.extract_info(story_url, download=False)
#         return info.get("url")  # To‘g‘ridan-to‘g‘ri yuklab olish linki


# # Test qilish
# story_link = "https://www.instagram.com/stories/fargona_tezkor/"
# download_url = get_instagram_story_url(story_link)

# print("Hikoya yuklab olish linki:", download_url)

# import instaloader

# def download_instagram_stories(username):
#     loader = instaloader.Instaloader()

#     # Instagram'ga login qilish
#     loader.load_session_from_file("abduvohid_dev")  # Avval login bo‘lib session saqlang

#     # Hikoyalarni yuklab olish
#     loader.download_stories(userids=[username])

# # Test
# print(download_instagram_stories("fargona_tezkor"))


# import yt_dlp

# def download_instagram_media(url, output_folder="downloads"):
#     ydl_opts = {
#         'outtmpl': f'{output_folder}/%(uploader)s/%(upload_date)s - %(title)s.%(ext)s',
#         'format': 'best',  # Eng yaxshi sifatdagi format
#         'merge_output_format': 'mp4,jpg',  # Videolar MP4, rasmlar JPG formatida
#         'embed-metadata': True,  # Metadata qo‘shish
#         'embed-thumbnail': True,  # Thumbnail qo‘shish
#         'cookies': 'cookies.txt',  # Agar kerak bo‘lsa, cookies orqali login qilish
#     }

#     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#         ydl.download([url])

# # Foydalanish: Instagram postining URL manzilini kiriting
# instagram_url = "https://www.instagram.com/p/DG-tRrgNnkv/?utm_source=ig_web_copy_link"
# download_instagram_media(instagram_url)


# import instaloader

# def get_story_links(username, password, target_username):
#     L = instaloader.Instaloader(
#         download_videos=False, 
#         download_pictures=False,
#         download_geotags=False,
#         download_comments=False,
#         save_metadata=False
#     )

#     # Login qilish
#     try:
#         L.login(username, password)
#         print("Instagramga muvaffaqiyatli login qilindi.")
#     except instaloader.exceptions.BadCredentialsException:
#         print("Xato: Login yoki parol noto‘g‘ri!")
#         return []
#     except instaloader.exceptions.TwoFactorAuthRequiredException:
#         print("Xato: Ikki faktorli autentifikatsiya yoqilgan, qo‘lda login qiling.")
#         return []

#     # Hikoyalarni olish
#     profile = instaloader.Profile.from_username(L.context, target_username)
    
#     # Yangi usul (2024)
#     stories = L.get_stories([profile.userid])
#     story_items = next(stories, None)
    
#     if not story_items:
#         print(f"{target_username} da hozircha hikoyalar mavjud emas.")
#         return []

#     story_links = []
#     for item in story_items.get_items():
#         if item.is_video:
#             story_links.append(item.video_url)
#         else:
#             story_links.append(item.url)
    
#     print(f"Topilgan hikoya linklari: {story_links}")
#     return story_links

    

# # LOGIN BILAN FOYDALANISH:
# your_username = "your_instagram_username"
# your_password = "your_instagram_password"
# target_user = "target_username"

# links = get_story_links("abduvohid_dev", "20042629Ab@", "fargona_tezkor")

# print("Hikoya fayllari yuklab olish linklari:")
# for link in links:
#     print(link)


# import requests
# import json
# from bs4 import BeautifulSoup

# # Instagram postining URL manzili
# POST_URL = "https://www.instagram.com/p/DHlg_abtePq/?utm_source=ig_web_copy_link"

# # Instagram sahifasini yuklab olish
# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
#     "Accept-Language": "en-US,en;q=0.9",
# }

# response = requests.get(POST_URL, headers=headers)
# if response.status_code == 200:
#     soup = BeautifulSoup(response.text, "html.parser")
#     print(soup)
#     # JavaScript ichida json formatdagi ma'lumotni topamiz
#     scripts = soup.find_all("script", type="application/ld+json")
#     json_data = None

#     for script in scripts:
#         try:
#             json_data = json.loads(script.string)
#             break  # JSON topilgach chiqib ketamiz
#         except:
#             continue
    
#     if json_data and "image" in json_data:
#         media_urls = json_data["image"]

#         if isinstance(media_urls, list):
#             print("📸 Albom rasmlari:")
#             for i, url in enumerate(media_urls, 1):
#                 print(f"{i}. {url}")
#         else:
#             print("🔗 Post rasmi:", media_urls)

#     else:
#         print("❌ Albom topilmadi yoki sahifa yuklanmadi.")

# else:
#     print("❌ Sahifani yuklab bo‘lmadi, status code:", response.status_code)


# import asyncio
# from playwright.async_api import async_playwright
# import time
POST_URL = "https://www.instagram.com/p/DHlg_abtePq/?utm_source=ig_web_copy_link"

# async def scrape_instagram():
#     async with async_playwright() as p:
#         current_time = time.time()
#         browser = await p.chromium.launch(headless=False)  # Headless Chrome
#         page = await browser.new_page()
#         await page.goto(POST_URL, timeout=9000)

#         # Postdagi media qismidagi rasmlarni olish
#         await page.wait_for_selector("img", timeout=10000)
#         images = await page.locator("img").all()
#         response = []
#         print("📸 Postdagi rasmlar:")
#         for i, img in enumerate(images, 1):
#             img_src = await img.get_attribute("src")
#             if img_src in response:
#                 continue
#             print(f"{i}. {img_src}")
#             response.append(img_src)
#         await browser.close()
#         print(current_time - time.time())
#         return response

# asyncio.run(scrape_instagram())



# import requests
# import time
# url = "https://insta-downloader5.p.rapidapi.com/instagram"

# querystring = {"insta_url":"https://www.instagram.com/reel/DHiB1gNNNYF/?utm_source=ig_web_copy_link"}

# headers = {
# 	"x-rapidapi-key": "54e518fa11msha164dc2cecb21c8p18d479jsn65ee0a8c6b70",
# 	"x-rapidapi-host": "insta-downloader5.p.rapidapi.com"
# }
# current_time = time.time()
# response = requests.get(url, headers=headers, params=querystring)
# print(current_time - time.time())
# print(response.json())
##########################################################################################


# asyncio.run(download_instagram_media("https://www.instagram.com/p/DHob-ZCufAH/?utm_source=ig_web_copy_link")) "video album"
# asyncio.run(download_instagram_media("https://www.instagram.com/reel/DHqlZQqokJT/?utm_source=ig_web_copy_link")) "video"
# asyncio.run(download_instagram_media("https://www.instagram.com/p/DHn_F9Lqd_Y/?utm_source=ig_web_copy_link")) # "image"
#################################################################












# from selenium import webdriver
# from selenium.webdriver.common.by import By
# import time

# POST_URL = "hhttps://www.instagram.com/p/DHJFvLGIZ03/?utm_source=ig_web_copy_link"

# options = webdriver.ChromeOptions()
# driver = webdriver.Chrome(options=options)

# driver.get(POST_URL)
# time.sleep(5) 


# images = driver.find_elements(By.CLASS_NAME, "_aagv")
# print(images)
# print("📸 Topilgan rasmlar:")
# for i, img in enumerate(images, 1):
#     print(f"{i}. {img.find_element(By.TAG_NAME, "img").get_attribute('src')}")

# driver.quit()

# from playwright.sync_api import sync_playwright

# def get_instagram_post_images(post_url):
#     """
#     Instagram postidagi faqat postga tegishli barcha rasm URLlarini olish (Playwright bilan)
    
#     Args:
#         post_url (str): Instagram post linki
        
#     Returns:
#         list: Postdagi rasm URLlari ro'yxati
#     """
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=False)  # Headless=True bo'lsa, brauzer ko'rinmaydi
#         page = browser.new_page()

#         try:
#             page.goto(post_url)
#             page.wait_for_selector("article", timeout=10000)  # Asosiy post yuklanishini kutish

#             # Faqat postning article qismi ichidagi rasm elementlarini topish
#             images = page.locator("article ._aagv img").all()

#             # URLlarni olish
#             image_urls = [img.get_attribute("src") for img in images]

#             for i, url in enumerate(image_urls, 1):
#                 print(f"{i}. {url}")
            
#             return image_urls

#         finally:
#             browser.close()

# POST_URL = "https://www.instagram.com/p/DHnkKP2IbPf/?utm_source=ig_web_copy_link"
# print(asyncio.run(get_instagram_post_images(POST_URL)))



# async def get_instagram_post_images(post_url):
#     """
#     Instagram postidagi barcha rasm URLlarini olish (albumlarni ham to'liq yuklash)
    
#     Args:
#         post_url (str): Instagram post linki
        
#     Returns:
#         list: Postdagi barcha rasm URLlari ro‘yxati
#     """
#     async with async_playwright() as p:  # ASYNC blok to‘g‘rilandi
#         browser = await p.chromium.launch(headless=False)
#         page = await browser.new_page()
#         await page.goto(post_url, timeout=60000)
#         await page.wait_for_selector("article", timeout=10000)  # Sahifa yuklanishini kutish

#         image_urls = set()  # Takrorlanmas URL to'plami
        
#         while True:
#             # Faqat postning article qismi ichidagi rasm elementlarini olish
#             images = await page.locator("article ._aagv img").all()
            
#             # Har bir rasmning URLini olish
#             for img in images:
#                 url = await img.get_attribute("src")  # AWAIT ishlatildi
#                 if url:
#                     image_urls.add(url)
            
#             # Keyingi slayderga o'tish tugmasi borligini tekshirish
#             next_button = page.locator("button[aria-label='Next']")
#             if await next_button.count() > 0:  # AWAIT ishlatildi
#                 await next_button.click()  # AWAIT ishlatildi
#                 await page.wait_for_timeout(2000)  # Rasmlar yuklanishini kutish
#             else:
#                 break  # Agar keyingi tugma yo‘q bo‘lsa, tsiklni to‘xtatish

#         for i, url in enumerate(image_urls, 1):
#             print(f"{i}. {url}")
        
#         await browser.close()
#         return list(image_urls)

# # TEST
# POST_URL = "https://www.instagram.com/p/DHVJnEyMvRO/?utm_source=ig_web_copy_link"
# asyncio.run(get_instagram_post_images(POST_URL))


# from selenium import webdriver
# from selenium.webdriver.common.by import By
# import time

# def get_instagram_post_images(post_url):
#     """
#     Instagram postidagi faqat postga tegishli barcha rasm URLlarini olish
    
#     Args:
#         post_url (str): Instagram post linki
        
#     Returns:
#         list: Postdagi rasm URLlari ro'yxati
#     """
#     driver = webdriver.Chrome()
    
#     try:
#         driver.get(post_url)
#         time.sleep(5)
        
#         article = driver.find_element(By.TAG_NAME, "article") 
        
#         images = article.find_elements(By.CLASS_NAME, "_aagv")
        
#         image_urls = [img.find_element(By.TAG_NAME, 'img').get_attribute('src') for img in images]

#         for i, url in enumerate(image_urls, 1):
#             print(f"{i}. {url}")
        
#         return image_urls

#     finally:
#         driver.quit()

# POST_URL = "https://www.instagram.com/p/DHqTt2HINxQ/?utm_source=ig_web_copy_link"
# get_instagram_post_images(POST_URL)



# import asyncio
# from playwright.async_api import async_playwright

# POST_URL = "https://www.instagram.com/p/DHqFbpSuzFG/?utm_source=ig_web_copy_link"

# async def scrape_instagram_album():
#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=False)  # Headless rejimni o'chirish
#         page = await browser.new_page()
#         await page.goto(POST_URL, timeout=60000)  # Sahifani ochish

#         image_urls = set()

#         while True:
#             try:
#                 # Hozirgi rasmni olish
#                 img_element = await page.query_selector("._aagv img")  # Klass nomi asosida olish
#                 if img_element:
#                     img_url = await img_element.get_attribute("src")
#                     if img_url and img_url not in image_urls:
#                         image_urls.add(img_url)
#                         print(f"📸 Rasm topildi: {img_url}")

#                 # "Next" tugmachasini bosish
#                 next_button = await page.query_selector("button._9zm2")  # Next tugmachasi klassi
#                 if next_button:
#                     await next_button.click()
#                     await page.wait_for_timeout(2000)  # Yangi rasm yuklanishini kutish
#                 else:
#                     break  # Agar "Next" bo'lmasa, loopdan chiqish

#             except Exception as e:
#                 print("❌ Xatolik:", e)
#                 break

#         await browser.close()

#         print("✅ Barcha rasmlar yuklandi!")
#         for i, url in enumerate(image_urls, start=1):
#             print(f"{i}. {url}")

# asyncio.run(scrape_instagram_album())


############################################################################









































    
#     except Exception as e:import requests
# from bs4 import BeautifulSoup

# def parse_snapins_ai(instagram_url):
#     session = requests.Session()
    
#     # Instagram post URL'ini Snapins API'ga yuborish
#     data = {
#         "url": instagram_url
#     }
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
#     }
    
#     response = session.post("https://snapins.ai", data=data, headers=headers)
#     print(response, 'res')
#     if response.status_code != 200:
#         print("Xatolik! Sahifa yuklanmadi.")
#         return []
    
#     # Sahifa HTML kodini parsing qilish
#     soup = BeautifulSoup(response.text, "html.parser")
    
#     # Media fayllarni olish
#     media_items = soup.select(".download-item a")
    
#     results = []
#     for item in media_items:
#         media_url = item.get("href")
        
#         # Fayl rasm yoki video ekanligini tekshirish
#         if media_url.endswith(".jpg") or media_url.endswith(".png"):
#             media_type = "image"
#         else:
#             media_type = "video"
        
#         results.append({"url": media_url, "type": media_type})
    
#     return results

# # Foydalanish
# instagram_post_url = "https://www.instagram.com/p/DHht6zEzMZB/?utm_source=ig_web_copy_link"
# media_links = parse_snapins_ai(instagram_post_url)

# print(media_links)
#         return {'error': f'Xato: {str(e)}'}

# POST_URL = "https://www.instagram.com/p/DG0PL0bsp1e/?utm_source=ig_web_copy_link"
# result = get_carousel_images(POST_URL)

# if 'images' in result:
#     print("📸 Albomdagi rasmlar:")
#     for i, url in enumerate(result['images'], 1):
#         print(f"{i}. {url}")
# else:
#     print(f"❌ Xato: {result.get('error')}")





#         driver.get("https://ssstik.io/en")
#         time.sleep(3)  


# from playwright.async_api import async_playwright
# import asyncio

# import time

# async def instgram_album_downloader(url):
#     async with async_playwright() as p:
#         curr = time.time()
#         browser = await p.chromium.launch(headless=False)
#         page = await browser.new_page()

#         try:
#             await page.goto("https://snapins.ai")

#             await page.fill("#url", url)
#             await page.click("#btn-submit")
    

#             await page.wait_for_selector(".download-item a", timeout=11900)

#             check_error = await page.locator("#alert").count()
#             print(check_error)
#             if check_error > 0:
#                 print("Xatolik")
#                 return []
           
#             download_links = await page.locator(".download-item a").all()

#             if not download_links:
#                 print(f"Hikoyalar topilmadi! ({url})")
#                 return []

#             urls = [await link.get_attribute("href") for link in download_links]
#             return urls

#         finally:
#             await browser.close()
#             print(time.time() - curr)

# # Asinxron ishga tushirish
# story_urls = asyncio.run(instgram_album_downloader("https://www.instagram.com/p/HVeg3Vos_p/?utm_source=ig_web_copy_link"))

# print(story_urls)


# import requests
# from bs4 import BeautifulSoup

# def parse_snapins_ai(instagram_url):
#     session = requests.Session()
    
#     # Instagram post URL'ini Snapins API'ga yuborish
#     data = {
#         "url": instagram_url
#     }
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
#     }
    
#     response = session.post("https://snapins.ai", data=data, headers=headers)
#     print(response, 'res')
#     if response.status_code != 200:
#         print("Xatolik! Sahifa yuklanmadi.")
#         return []
    
#     # Sahifa HTML kodini parsing qilish
#     soup = BeautifulSoup(response.text, "html.parser")
    
#     # Media fayllarni olish
#     media_items = soup.select(".download-item a")
    
#     results = []
#     for item in media_items:
#         media_url = item.get("href")
        
#         # Fayl rasm yoki video ekanligini tekshirish
#         if media_url.endswith(".jpg") or media_url.endswith(".png"):
#             media_type = "image"
#         else:
#             media_type = "video"
        
#         results.append({"url": media_url, "type": media_type})
    
#     return results

# # Foydalanish
# instagram_post_url = "https://www.instagram.com/p/DHht6zEzMZB/?utm_source=ig_web_copy_link"
# media_links = parse_snapins_ai(instagram_post_url)

# print(media_links)







# from playwright.async_api import async_playwright
# import asyncio
# import time

# async def instagram_album_downloader(url):
#     async with async_playwright() as p:
#         curr = time.time()
#         browser = await p.chromium.launch(headless=False)  # headless=False -> Brauzerni ko‘rsatish
#         page = await browser.new_page()

#         try:
#             await page.goto("https://snapins.ai")

#             # URL kiritish va tugmani bosish
#             await page.fill("#url", url)
#             await page.click("#btn-submit")

#             # Xatolik borligini tekshirish
#             try:
#                 await page.wait_for_selector("#alert", timeout=5000)  # 5 soniya kutish
#                 check_error = await page.locator("#alert").count()
#                 if check_error > 0:
#                     print("Xatolik! Albom yuklab bo‘lmadi.")
#                     return []
#             except Exception:
#                 pass  # Agar alert chiqmasa, davom etamiz

#             # Yuklab olish tugmalari chiqishini kutish
#             await page.wait_for_selector(".download-item a", timeout=15000)  # 15 soniya kutish

#             # Linklarni olish
#             download_links = await page.locator(".download-item a").all()
#             if not download_links:
#                 print(f"Hikoyalar topilmadi! ({url})")
#                 return []

#             urls = [await link.get_attribute("href") for link in download_links]
#             return urls

#         finally:
#             await browser.close()
#             print("Ish vaqti:", time.time() - curr)

# # Asinxron ishga tushirish
# story_urls = asyncio.run(instagram_album_downloader("https://www.instagram.com/p/HVeg3Vos_p/?utm_source=ig_web_copy_link"))

# print("Yuklangan fayllar:", story_urls)



# from insta import get_instagram_story_urls


# import asyncio
# print(asyncio.run(get_instagram_story_urls("https://www.instagram.com/stories/shayk.hulislamova/")))
# print(asyncio.run(get_instagram_story_urls("https://www.instagram.com/stories/sardor.salimjanov/3597788380524588838/")))



# from TikTokApi import TikTokApi

# api = TikTokApi()
# video_url = "https://vt.tiktok.com/ZSrLJ2KnQ/"
# vide_data = api.video(url=video_url).bytes()
# with open("video.mp4", "wb") as f:
#     f.write(vide_data)

# import yt_dlp

# def get_tiktok_video(url):
#     ydl_opts = {
#         "quiet": True,
#         "extract_flat": True,
#     }
#     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#         info = ydl.extract_info(url, download=False)
#         return info
    
# video_url = "https://vt.tiktok.com/ZSrLJ2KnQ/"
# info = get_tiktok_video(video_url)
# print(info)

# import subprocess

# def get_tiktok_video_url(video_url):
#     cmd = ["tiktok-scraper", "video", video_url, "-d"]
#     result = subprocess.run(cmd, capture_output=True, text=True)
#     return result.stdout.strip()

# video_url = "https://vt.tiktok.com/ZSrLJ2KnQ/"
# direct_link = get_tiktok_video_url(video_url)
# print("Direct Video URL:", direct_link)

#
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import requests
from bs4 import BeautifulSoup
#
# # setup chrome driver
# driver = webdriver.Chrome()
#
#
# # open to web page
# driver.get("https://www.instagram.com/")
#
#
# username = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']")))
# password = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))
# username.clear()
# username.send_keys("abduvohid_dev")
# password.clear()
# password.send_keys("20042629Ab@")
#
# button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
# button.click()
#
# # Qidiruv qismi
# WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "svg[aria-label='Search']"))).click()
#
# searchbox = WebDriverWait(driver, 10).until(
#     EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Search']"))
# )
#
# keyboard = "@abduvohid_2629"
# searchbox.clear()
# searchbox.send_keys(keyboard)
#
# if keyboard.startswith("@"):
#     keyboard = keyboard[1:]
# first_result = WebDriverWait(driver, 10).until(
#     EC.element_to_be_clickable((By.XPATH, f'//span[text()="{keyboard}"]'))
# )
#
# first_result.click()
#
# initial_height = driver.execute_script("return document.body.scrollHeight")
#
# soups = []
#
# while True:
#     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#     time.sleep(2)
#
#     html = driver.page_source
#     soups.append(BeautifulSoup(html, "html.parser"))
#
#     current_height = driver.execute_script("return document.body.scrollHeight")
#
#     if current_height == initial_height:
#         break
#     initial_height = current_height
#
# posts_urls = []
#
# for soup in soups:
#     elements = soup.find_all("a",
#                              class_="x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz _a6hd")
#
#     posts_urls.extend([
#         element['href'] for element in elements
#         if element.get('href') and any(x in element['href'] for x in ["/p/", "/reel/"])
#     ])
#
# unique_posts_urls = list(set(posts_urls))
# print(len(unique_posts_urls))








# def func(post_url):
#     options = Options()
#     options.add_argument("--start-maximized")
#     driver = webdriver.Chrome(options=options)
#
#     # URL orqali ochish
#     driver.get(post_url)
#
#     # --- 2. Parse HTML ---
#     time.sleep(3)  # Sahifa to'liq yuklanishini kutish
#
#     soup = BeautifulSoup(driver.page_source, "html.parser")
#
#     media_urls = []
#
#     video = soup.find("video")
#     print(video, "Video")
#     if video and video.has_attr("src"):
#         media_urls.append(video["src"])
#     else:
#         img_tags = soup.find_all("img")
#         for img in img_tags:
#             if img.has_attr("src") and "scontent" in img["src"]:  # faqat rasm URL
#                 media_urls.append(img["src"])
#
#     # --- 4. Natija va Media URL'larini chiqarish ---
#     if media_urls:
#         print("✅ Media URL lar:")
#         for url in media_urls:
#             print(url)
#     else:
#         print("❌ Media topilmadi.")
#
#     driver.quit()
#
# print(func(post_url="https://www.instagram.com/reel/DIWWW-TsHjg/?utm_source=ig_web_copy_link"))
#


import logging
logger = logging.getLogger(__name__)

from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

# async def get_instagram_post_images(post_url, caption, proxy_config):
#     """
#     Instagram postidagi barcha rasm URLlarini olish (albumlarni ham to'liq yuklash)
#
#     Args:
#         post_url (str): Instagram post linki
#
#     Returns:
#         dict: Instagram postidagi barcha rasm URLlari va qo‘shimcha ma‘lumotlar
#     """
#     try:
#         async with async_playwright() as playwright:
#             browser = await playwright.chromium.launch()
#             try:
#                 page = await browser.new_page()
#             except Exception as e:
#                 logger.error(msg=f"Page yaratishda xatolik:: {e}")
#                 return {"error": True, "message": "Invalid response from the server"}
#
#             try:
#                 await page.goto(post_url, timeout=15000)
#             except PlaywrightTimeoutError:
#                 logger.error(msg=f"⏳ Sahifani yuklash muddati tugadi")
#                 return {"error": True, "message": "Invalid response from the server"}
#
#             path = urlparse(post_url).path
#             shortcode = path.strip("/").split("/")[-1]
#
#             try:
#                 await page.wait_for_selector("article", timeout=15000)
#             except PlaywrightTimeoutError:
#                 logger.error(msg=f"🔄 Sahifada article elementi topilmadi")
#                 return {"error": True, "message": "Invalid response from the server"}
#
#             image_urls = set()
#
#             while True:
#                 images = await page.locator("article ._aagv img").all()
#                 for img in images:
#                     url = await img.get_attribute("src")
#                     if url and (url.startswith('http') and any(ext in url for ext in ['.jpg', '.jpeg', '.png'])):
#                         image_urls.add(url)
#
#                 next_button = page.locator("button[aria-label='Next']")
#                 if await next_button.count() > 0:
#                     prev_count = len(image_urls)
#                     await next_button.click()
#                     await page.wait_for_selector("article ._aagv img", timeout=5000)  # Ensure new images are loaded
#                     if len(image_urls) == prev_count:
#                         break  # Agar yangi rasm topilmasa, loopni to‘xtatish
#                 else:
#                     break
#
#             if not image_urls:
#                 logger.error(msg="🚫 Rasm URLlari topilmadi")
#                 return {"error": True, "message": "Invalid response from the server"}
#
#             return {
#                 "error": False,
#                 "hosting": "instagram",
#                 "type": "album" if len(image_urls) > 1 else "image",
#                 "shortcode": shortcode,
#                 "caption": caption,
#                 "medias": [{"type": "image", "download_url": url, "thumb": url} for url in image_urls]
#             }
#
#     except Exception as e:
#         logger.error(msg=f"❌ Noma'lum xatolik: {str(e)}")
#         return {"error": True, "message": "Invalid response from the server"}
#
# import asyncio
# print(asyncio.run(get_instagram_post_images(post_url="https://www.instagram.com/reel/DG3A3BiqzV5/?utm_source=ig_web_copy_link", caption="SAlom", proxy_config=None)))


import asyncio
from urllib.parse import urlparse
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError



# async def get_instagram_post_images(post_url: str, caption: str = "", proxy_config: dict = None):
#     """
#     Instagram postidagi barcha rasm URLlarini olish (albumlarni ham to'liq yuklash)
#     """
#     playwright = await async_playwright().start()
#     browser = None
#
#     try:
#         browser_args = {
#             "headless": False
#         }
#
#         if proxy_config:
#             browser_args["proxy"] = proxy_config
#
#         browser = await playwright.chromium.launch(**browser_args)
#         context = await browser.new_context()
#         page = await context.new_page()
#
#         try:
#             await page.goto(post_url, timeout=15000)
#         except PlaywrightTimeoutError:
#             return {"error": True, "message": "⏳ Sahifani yuklash muddati tugadi"}
#
#         path = urlparse(post_url).path
#
#         try:
#             await page.wait_for_selector("article", timeout=15000)
#         except PlaywrightTimeoutError:
#             logger.error("🔄 Sahifada article elementi topilmadi")
#             return {"error": True, "message": "Invalid response from the server"}
#
#         image_urls = set()
#         await page.mouse.click(10, 10)
#         await page.wait_for_timeout(1500)
#
#         while True:
#             images = await page.locator("article ._aagv img").all()
#             for img in images:
#                 url = await img.get_attribute("src")
#                 if url:
#                     image_urls.add(url)
#
#             next_button = page.locator("button[aria-label='Next']")
#
#             # "Next" tugmasi mavjud bo'lishini kutamiz
#             try:
#                 await next_button.wait_for(timeout=3000)
#             except PlaywrightTimeoutError:
#                 break  # Endi keyingi rasm yo‘q
#
#             prev_count = len(image_urls)
#             await next_button.click()
#             await page.wait_for_timeout(1000)  # Keyingi rasm yuklanishini kutamiz
#
#             # await page.wait_for_selector("video, img", timeout=10000)  # Video va img kutish
#
#             video_elements = await page.query_selector_all("video")
#             video_data = []
#             for video in video_elements:
#                 video_url = await video.get_attribute("src")
#                 if video_url:  # Agar URL mavjud bo'lsa
#                     video_data.append({"url": video_url, "type": "video"})
#
#             # Agar yangi rasm chiqmagan bo‘lsa, loopdan chiqamiz
#             images = await page.locator("article ._aagv img").all()
#             new_urls = {await img.get_attribute("src") for img in images if await img.get_attribute("src")}
#             if len(new_urls - image_urls) == 0:
#                 break
#             image_urls.update(new_urls)
#
#         if not image_urls:
#             logger.error(msg="🚫 Rasm URLlari topilmadi")
#             return {"error": True, "message": "Invalid response from the server"}
#
#         return {
#             "error": False,
#             "hosting": "instagram",
#             "type": "album" if len(image_urls) > 1 else "image",
#             "caption": caption,
#             "medias": [{"type": "image", "download_url": url} for url in image_urls]
#         }
#
#
#     finally:
#         # Brauzer va Playwright sessionni toza yopish
#         if browser:
#             await browser.close()
#         await playwright.stop()


# async def get_instagram_post_images(post_url: str, proxy_config: dict = None):
#     """
#     Instagram postidagi barcha rasm va video URLlarini olish (albumlarni ham to'liq yuklash)
#     """
#     playwright = await async_playwright().start()
#     browser = None

#     try:
#         browser_args = {
#             "headless": False
#         }

#         if proxy_config:
#             browser_args["proxy"] = proxy_config

#         browser = await playwright.chromium.launch(**browser_args)
#         context = await browser.new_context()
#         page = await context.new_page()

#         try:
#             await page.goto(post_url, timeout=15000)
#         except PlaywrightTimeoutError:
#             return {"error": True, "message": "⏳ Sahifani yuklash muddati tugadi"}


#         try:
#             await page.wait_for_selector("article", timeout=15000)
#         except PlaywrightTimeoutError:
#             logger.error("🔄 Sahifada article elementi topilmadi")
#             return {"error": True, "message": "Invalid response from the server"}

#         image_urls = set()
#         video_data = []

#         await page.mouse.click(10, 10)
#         await page.wait_for_timeout(1500)
#         caption = None
#         caption_element = await page.query_selector('article span._ap3a')
#         if caption_element:
#             caption = await caption_element.inner_text()

#         while True:
#             # Rasmlar
#             images = await page.locator("article ._aagv img").all()
#             for img in images:
#                 url = await img.get_attribute("src")
#                 if url:
#                     image_urls.add(url)

#             # Videolar
#             video_elements = await page.query_selector_all("video")
#             for video in video_elements:
#                 video_url = await video.get_attribute("src")
#                 if video_url and not any(v["url"] == video_url for v in video_data):
#                     video_data.append({"url": video_url, "type": "video"})

#             # Keyingi tugmasini aniqlash
#             next_button = page.locator("button[aria-label='Next']")
#             try:
#                 await next_button.wait_for(timeout=3000)
#             except PlaywrightTimeoutError:
#                 break  # Endi keyingi media yo‘q

#             prev_count = len(image_urls) + len(video_data)

#             await next_button.click()
#             await page.wait_for_timeout(1000)

#             # Yangi rasm yoki video chiqmagan bo‘lsa, to‘xtaymiz
#             images = await page.locator("article ._aagv img").all()
#             new_urls = {await img.get_attribute("src") for img in images if await img.get_attribute("src")}
#             new_video_elements = await page.query_selector_all("video")
#             new_video_urls = [
#                 await video.get_attribute("src") for video in new_video_elements if await video.get_attribute("src")
#             ]
#             for url in new_video_urls:
#                 if url and not any(v["url"] == url for v in video_data):
#                     video_data.append({"url": url, "type": "video"})

#             if len(new_urls - image_urls) == 0 and len(new_video_urls) == 0:
#                 break

#             image_urls.update(new_urls)

#         if not image_urls and not video_data:
#             logger.error(msg="🚫 Media URLlari topilmadi")
#             return {"error": True, "message": "Invalid response from the server"}

#         media_items = [{"type": "image", "download_url": url} for url in image_urls]
#         media_items += video_data  # videolarni ham qo‘shamiz

#         return {
#             "error": False,
#             "hosting": "instagram",
#             "type": "album" if len(media_items) > 1 else media_items[0]["type"],
#             "caption": caption,
#             "medias": media_items
#         }

#     finally:
#         if browser:
#             await browser.close()
#         await playwright.stop()

# 🔍 Sinab ko‘rish (Asosiy)
# if __name__ == "__main__":
#     # post_link = "   "  # Misol post
#     post_link = "https://www.instagram.com/p/DIB8oINAbCk/?utm_source=ig_web_copy_link"
#     result = asyncio.run(get_instagram_post_images(post_link, None))
#     print(result)




# import asyncio
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from webdriver_manager.chrome import ChromeDriverManager
# from concurrent.futures import ThreadPoolExecutor
# import time

# # Selenium jarayonini ishga tushirish
# def run_selenium(url):
#     options = Options()
#     options.add_argument("--headless")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.binary_location = "/usr/bin/chromium"  # yoki /usr/bin/google-chrome

#     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
#     driver.get("https://snaptik.app")
#     time.sleep(2)
    
#     body = driver.find_element(By.TAG_NAME, "body")
#     body.send_keys(Keys.ESCAPE)

#     input_box = driver.find_element(By.NAME, "url")
#     input_box.send_keys(url)

#     driver.find_element(By.XPATH, "//button[@type='submit' and @aria-label='Get']").click()
#     time.sleep(5)

#     try:
#         driver.find_element(By.CLASS_NAME, "video-links")
#         video_links_divs = driver.find_elements(By.CLASS_NAME, "video-links")
        
#         for div in video_links_divs:
#             try:
#                 a_tag = div.find_element(By.TAG_NAME, "a")
#                 video_url = a_tag.get_attribute("href")
#                 print("✅ Topilgan video link:", video_url)
#             except:
#                 print("⚠️ <a> tag topilmadi bu div ichida.")
#     except:
#         print("❌ Video linklar topilmadi. Balki sayt bloklagan yoki link noto‘g‘ri.")
    
#     driver.quit()

# # Async wrapper
# async def main(urls):
#     with ThreadPoolExecutor() as executor:
#         tasks = []
#         for url in urls:
#             task = asyncio.get_event_loop().run_in_executor(executor, run_selenium, url)
#             tasks.append(task)
#         await asyncio.gather(*tasks)


# if __name__ == "__main__":
#     urls = ["https://vt.tiktok.com/ZSr9A2KyN/"]
#     asyncio.run(main(urls))



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

# async def download_from_snaptik(url):
#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=True)
#         context = await browser.new_context()
#         page = await context.new_page()
#         try:
#             await page.goto("https://snaptik.app", timeout=15000)
#             await page.wait_for_timeout(1000)
#             await page.mouse.click(10, 10)  # Ekranning chap yuqori burchagiga klik
#             await page.fill("input[name='url']", url)
#             await page.click("button[type='submit'][aria-label='Get']")
#             await page.wait_for_timeout(2000)
#
#             video_links_divs = await page.query_selector_all(".video-links")
#             if not video_links_divs:
#                 print("❌ Video linklar topilmadi. Sayt bloklagan yoki link noto‘g‘ri.")
#                 return
#             image_links_divs = await page.query_selector_all(".is-multiline")
#             if not image_links_divs:
#                 print("❌ Video linklar topilmadi. Sayt bloklagan yoki link noto‘g‘ri.")
#                 return
#             for img in image_links_divs:
#                 img_tag = await img.query_selector_all("img")
#                 if  img_tag:
#                     src = await img_tag.get_attribute("src")
#
#
#             else:
#                 for div in video_links_divs:
#                     a_tag = await div.query_selector("a")
#                     if a_tag:
#                         href = await a_tag.get_attribute("href")
#                         # print("✅ Topilgan video link:", href)
#                         return {
#                             "error": False,
#                             "url": url,
#                             "type": "video",
#                             "hosting": "tiktok",
#                             "medias": [
#                                 {
#                                     "download_url": href,
#                                     "type": "video"
#                                 }
#                             ]
#                         }
#                     else:
#                         print("⚠️ <a> tag topilmadi bu div ichida.")
#         except Exception as e:
#             print("❌ Xatolik:", e)
#
#
#         await browser.close()