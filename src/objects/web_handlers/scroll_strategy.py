from __future__ import annotations

import time
from abc import ABC

from bs4 import BeautifulSoup

from objects.file_handlers.log_writer import LogWriter
from objects.web_handlers.driver_handler import DriverHandler
from objects.web_handlers.web_handler import WebHandler
from settings.web_handlers_defaults import *


class ScrollStrategy(WebHandler, ABC):
    pass


class NoScroll(ScrollStrategy):
    def __init__(self):
        pass

    def handle(self, driver: DriverHandler, soup: BeautifulSoup, attempt: int) -> None:
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

    def handle(self, driver: DriverHandler, soup: BeautifulSoup, attempt: int) -> None:
        last_height = driver.execute("return document.body.scrollHeight")
        for i in range(self.scroll_max_attempts):
            if hasattr(driver.unsafe_driver_get(), "scroll_to_bottom"):
                driver.unsafe_driver_get().scroll_to_bottom()
            else:
                driver.execute("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(self.scroll_pause_time)
            new_height = driver.execute("return document.body.scrollHeight")
            if new_height == last_height:
                self.logger.debug(f"Finished scrolling at {i + 1} attempt")
                return
            last_height = new_height
        self.logger.debug(f"All scroll attempts exhausted {self.scroll_max_attempts}")


class LimitedScroll(ScrollStrategy):
    def __init__(
        self,
        log_writer: LogWriter,
        scroll_pause_time: float = SCROLL_PAUSE_TIME,
        scroll_times: int = SCROLL_MAX_ATTEMPTS,
        scroll_by: int = SCROLL_BY,
    ):
        self.logger = log_writer.get_logger(type(self).__name__)
        self.scroll_pause_time = scroll_pause_time
        self.scroll_times = scroll_times
        self.scroll_by = scroll_by

    def handle(self, driver: DriverHandler, soup: BeautifulSoup, attempt: int) -> None:
        for i in range(self.scroll_times):
            driver.execute(f"window.scrollTo(0, {self.scroll_by * (i + 1)});")
            time.sleep(self.scroll_pause_time)
