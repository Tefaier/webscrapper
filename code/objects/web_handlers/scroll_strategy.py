from __future__ import annotations

import time
from abc import ABC

from bs4 import BeautifulSoup
from selenium.webdriver.chrome.webdriver import WebDriver

from objects.file_handlers.log_writer import LogWriter
from objects.web_handlers.web_handler import WebHandler
from settings.web_handlers_defaults import *


class ScrollStrategy(WebHandler, ABC):
    pass


class NoScroll(ScrollStrategy):
    def __init__(self):
        pass

    def handle(self, driver: WebDriver, soup: BeautifulSoup) -> None:
        return


class BottomScroll(ScrollStrategy):
    def __init__(
        self,
        log_writer: LogWriter,
        scroll_pause_time: float = SCROLL_PAUSE_TIME,
        scroll_max_attempts: int = SCROLL_MAX_ATTEMPTS,
    ):
        self.logger = log_writer.get_logger(type(self).__name__)
        self.scroll_pause_time = scroll_pause_time
        self.scroll_max_attempts = scroll_max_attempts

    def handle(self, driver: WebDriver, soup: BeautifulSoup) -> None:
        last_height = driver.execute_script("return document.body.scrollHeight")
        for i in range(self.scroll_max_attempts):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(self.scroll_pause_time)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                self.logger.debug(f"Finished scrolling at {i + 1} attempt")
                break
            last_height = new_height
        self.logger.debug(f"All scroll attempts exhausted {self.scroll_max_attempts}")
