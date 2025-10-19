from __future__ import annotations

import time
from typing import Optional, List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, PageElement
from selenium.webdriver.chrome.webdriver import WebDriver

from objects.elements.elements_collector import ElementsCollector
from objects.elements.elements_orchestra import ElementsOrchestra
from objects.types.custom_exceptions import TargetNotFoundException
from objects.web_handlers.block_screen_handler import BlockScreenHandler, NoHandling
from objects.web_handlers.scroll_strategy import ScrollStrategy, NoScroll
from objects.web_handlers.reload_handler import ReloadHandler
from settings import (
    MAX_OPEN_ATTEMPTS,
    max_page_load_time,
    page_load_check_intervals,
    wait_before_reading as waiting_time,
)


class ContentParser:
    """
    New parser based on old Process logic.

    Responsibilities:
    - Open a URL either via requests or an existing Selenium WebDriver (if provided).
    - If Chrome (driver) is used, apply BlockScreenHandler and ScrollStrategy.
    - Use ElementsOrchestra to collect, validate and write page content.
    - Use a dedicated ElementsCollector to retrieve the link to the next page.

    All collaborators (orchestra, next_link_collector, scroll_strategy, block_handler, driver) are
    provided via the constructor to keep this class decoupled and testable.
    """

    def __init__(
        self,
        orchestra: ElementsOrchestra,
        next_link_collector: ElementsCollector,
        driver=None,
        scroll_strategy: Optional[ScrollStrategy] = None,
        block_handler: Optional[BlockScreenHandler] = None,
        reload_handler: Optional[ReloadHandler] = None,
    ) -> None:
        self.orchestra = orchestra
        self.next_link_collector = next_link_collector
        self.driver: WebDriver = driver
        self.scroll_strategy: ScrollStrategy = scroll_strategy or NoScroll()
        self.block_handler: BlockScreenHandler = block_handler or NoHandling()
        self.current_url: Optional[str] = None
        self.reload_handler: ReloadHandler = reload_handler or ReloadHandler(
            wait_before_open=False,
            sleep_before_open_seconds=0.0,
            wait_before_process=True,
            sleep_before_process_seconds=waiting_time or 0.0,
            max_attempts=MAX_OPEN_ATTEMPTS,
            max_page_load_wait_seconds=max_page_load_time,
            page_load_check_interval_seconds=page_load_check_intervals,
        )

    # ------------------------
    # Public API
    # ------------------------
    def parse_content(self, url: str):
        self.current_url = url
        self.reload_handler.run(self)

    def set_driver(self, driver: WebDriver):
        self.driver = driver

    # ------------------------
    # Internal helpers
    # ------------------------
    def _write_content(self):
        self.orchestra.run(self.current_url, self._get_soup(self.current_url))

    def _using_chrome(self) -> bool:
        return self.driver is not None

    def _get_soup(self, url: str) -> BeautifulSoup:
        if self._using_chrome():
            html = self.driver.page_source
        else:
            r = requests.get(url)
            try:
                html = r.content.decode("utf8")
            except Exception:
                html = r.text
        return BeautifulSoup(html, "html.parser")

    def _current_dom(self) -> BeautifulSoup:
        if self._using_chrome():
            return BeautifulSoup(self.driver.page_source, "html.parser")
        raise RuntimeError("_current_dom called without chrome driver")

    def _handle_block_and_scroll(self, soup: BeautifulSoup):
        if not self._using_chrome():
            return
        # 1) Try to bypass blocking screens (input/click) using provided handler
        try:
            self.block_handler.handle(self.driver, soup)
        except TargetNotFoundException:
            # Not found elements to handle; proceed
            pass

        # After possible interactions, DOM likely changed
        soup = self._current_dom()

        # 2) Apply scrolling strategy (e.g., load dynamic content)
        self.scroll_strategy.handle(self.driver, soup)


    def _refresh_current(self, url: str) -> None:
        if not self._using_chrome():
            time.sleep(page_load_check_intervals)
            return
        try:
            # Simple refresh logic similar to the old flow
            self.driver.delete_all_cookies()
            self.driver.refresh()
        except Exception:
            # As a fallback, try to re-open the url
            try:
                self.driver.get(url)
            except Exception:
                pass

    def _get_next_link(self, current_url: str, soup: BeautifulSoup) -> Optional[str]:
        candidates: List[PageElement] = self.next_link_collector.collect(soup) or []
        if len(candidates) == 0:
            return None
        link_el = candidates[0]
        href = link_el.get("href") if hasattr(link_el, "get") else None
        if not href:
            return None
        # Build absolute url using current page context
        if href.startswith("javascript"):
            return href
        return urljoin(current_url, href)
