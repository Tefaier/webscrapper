from __future__ import annotations

import time
from abc import ABC

from bs4 import BeautifulSoup
from selenium.webdriver.chrome.webdriver import WebDriver

from .web_handler import WebHandler


class ScrollStrategy(WebHandler, ABC):
    pass


class NoScroll(ScrollStrategy):
    def handle(self, driver: WebDriver, soup: BeautifulSoup) -> None:
        return


class BottomScroll(ScrollStrategy):
    def __init__(self, scroll_pause_time: int, scroll_max_attempts: int):
        self.scroll_pause_time = scroll_pause_time
        self.scroll_max_attempts = scroll_max_attempts

    def handle(self, driver: WebDriver, soup: BeautifulSoup) -> None:
        last_height = driver.execute_script("return document.body.scrollHeight")
        for i in range(self.scroll_max_attempts):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(self.scroll_pause_time)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
