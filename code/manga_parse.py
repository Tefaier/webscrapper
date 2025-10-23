import os
import time
from concurrent.futures.thread import ThreadPoolExecutor
from concurrent.futures import wait

from trio import sleep_until

from old_flow import Process
from bs4 import BeautifulSoup
import urllib.request
import cv2


def download_image_urllib(url, filename):
    print(f"Image started loading: {filename}")
    try:
        urllib.request.urlretrieve(url, filename)
        print(f"Image successfully downloaded: {filename}")
    except Exception as e:
        print(f"Error downloading image: {e}")


pool = ThreadPoolExecutor(max_workers=100)

start_url = ""
create_path = lambda chapter, id: str(chapter) + "-" + str(id) + ".png"

process = Process({"chrome": True, "chrome_undetected": True, "wait": True})
for chapter in range(71, 78):
    for i in range(10):
        try:
            if i == 0:
                soup = process.get_soup(start_url)
            else:
                soup = process.refresh(start_url)
            holder = soup.find("div", {"class": "container-reader-chapter"})
            imgs = holder.find_all("img")
            break
        except:
            pass
    urls = [img["data-src"] for img in imgs]
    futures = []
    for i, url in enumerate(urls):
        futures.append(pool.submit(download_image_urllib, url, create_path(chapter, i)))
    wait(futures)
    loaded = []
    for i in range(0, len(urls)):
        if os.path.exists(create_path(chapter, i)):
            loaded.append(cv2.imread(create_path(chapter, i)))
    result = cv2.vconcat(loaded)
    cv2.imwrite(str(chapter) + ".png", result)
    for i in range(0, len(urls)):
        if os.path.exists(create_path(chapter, i)):
            os.remove(create_path(chapter, i))

    process.press_element(soup.find("a", {}))
    start_url = process._driver_handler_name.current_url
