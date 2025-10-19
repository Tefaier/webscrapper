from __future__ import annotations

import time
from typing import Optional, TYPE_CHECKING, Callable

from bs4 import BeautifulSoup
from selenium.webdriver.chrome.webdriver import WebDriver

from objects.types.custom_exceptions import TargetNotFoundException, MaxOpeningTimeExceededException
from objects.web_handlers.driver_handler import DriverHandler
from settings import (
    MAX_OPEN_ATTEMPTS as DEFAULT_MAX_OPEN_ATTEMPTS,
    max_page_load_time as DEFAULT_MAX_PAGE_LOAD_TIME,
    page_load_check_intervals as DEFAULT_PAGE_LOAD_CHECK_INTERVAL,
    wait_before_reading as DEFAULT_WAIT_BEFORE_READING,
)

if TYPE_CHECKING:
    # Only for type hints to avoid circular imports at runtime
    from objects.parsing_handlers.content_parser import ContentParser


class ReloadHandler:
    """
    Encapsulates page reloading/opening logic with configurable behavior.

    This handler delegates to a provided ContentParser instance for:
    - opening URL and building soup
    - obtaining current DOM
    - refreshing the page
    - running the content orchestra and computing next link

    Configuration options allow controlling waits and retry behavior.
    """

    def __init__(
        self,
        driver_creator: DriverHandler = None,
        wait_before_open: bool = False,
        sleep_before_open_seconds: float = 0.0,
        wait_before_process: bool = True,
        sleep_before_process_seconds: float = DEFAULT_WAIT_BEFORE_READING or 0.0,
        max_attempts: int = DEFAULT_MAX_OPEN_ATTEMPTS,
        max_page_load_wait_seconds: float = DEFAULT_MAX_PAGE_LOAD_TIME,
        page_load_check_interval_seconds: float = DEFAULT_PAGE_LOAD_CHECK_INTERVAL,
    ) -> None:
        self.driver_creator = driver_creator
        self.wait_before_open = wait_before_open
        self.sleep_before_open_seconds = sleep_before_open_seconds
        self.wait_before_process = wait_before_process
        self.sleep_before_process_seconds = sleep_before_process_seconds
        self.max_attempts = max_attempts
        self.max_page_load_wait_seconds = max_page_load_wait_seconds
        self.page_load_check_interval_seconds = page_load_check_interval_seconds

    # ------------------------
    # Public API
    # ------------------------
    def run(self, parser: ContentParser):
        """Attempt to open and process a page with reload/wait logic. Raises MaxOpeningTimeExceededException if failed all attempts"""
        attempts = 0
        if self.wait_before_open and self.sleep_before_open_seconds and self.sleep_before_open_seconds > 0:
            time.sleep(self.sleep_before_open_seconds)

        while attempts <= self.max_attempts:
            attempts += 1
            if self._attempt_once(parser):
                return
            if parser._using_chrome() and (self.max_page_load_wait_seconds or 0) > 0:
                deadline = time.time() + float(self.max_page_load_wait_seconds)
                while time.time() < deadline:
                    time.sleep(self.page_load_check_interval_seconds)
                    if self._attempt_once(parser):
                        return
            self._perform_refresh(parser, attempts)

        raise MaxOpeningTimeExceededException("Seemed to fail overcoming defence")

    # ------------------------
    # Internal helpers
    # ------------------------
    def _attempt_once(self, parser: ContentParser) -> bool:
        """Single attempt to open/process the page. Returns whether operation succeeded"""
        if parser._using_chrome():
            soup = parser._get_soup(parser.current_url)
            parser._handle_block_and_scroll(soup)
            self._maybe_wait_before_process()

        try:
            parser._write_content()
            return True
        except TargetNotFoundException:
            return False

    def _maybe_wait_before_process(self) -> None:
        if self.wait_before_process and self.sleep_before_process_seconds and self.sleep_before_process_seconds > 0:
            time.sleep(self.sleep_before_process_seconds)

    def _perform_refresh(self, parser: ContentParser, attempt: int):
        if not parser._using_chrome():
            return
        if attempt < self.max_attempts:
            parser.driver.delete_all_cookies()
            parser.driver.refresh()
        else:
            url = parser.driver.current_url
            parser.set_driver(self.driver_creator.create_driver())
            parser.driver.get(url)
