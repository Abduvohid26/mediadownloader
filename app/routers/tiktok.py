# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.keys import Keys
# from webdriver_manager.chrome import ChromeDriverManager
# import time

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
