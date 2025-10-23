from __future__ import annotations

import time
from typing import Optional, List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, PageElement
from selenium.webdriver.chrome.webdriver import WebDriver

from objects.elements.elements_collector import ElementsCollector
from objects.elements.elements_orchestra import ElementsOrchestra
from objects.file_handlers.log_writer import LogWriter
from objects.types.custom_exceptions import TargetNotFoundException
from objects.web_handlers.block_screen_handler import BlockScreenHandler, NoHandling
from objects.web_handlers.driver_handler import DriverHandler
from objects.web_handlers.scroll_strategy import ScrollStrategy, NoScroll
from objects.web_handlers.reload_handler import ReloadHandler


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
        log_writer: LogWriter,
        orchestra: ElementsOrchestra,
        scroll_strategy: ScrollStrategy,
        block_handler: BlockScreenHandler,
        reload_handler: ReloadHandler,
        driver_handler: DriverHandler = None,
    ) -> None:
        self.logger = log_writer.get_logger(type(self).__name__)
        self.orchestra = orchestra
        self.scroll_strategy: ScrollStrategy = scroll_strategy
        self.block_handler: BlockScreenHandler = block_handler
        self.reload_handler: ReloadHandler = reload_handler
        self.driver_handler = driver_handler
        self.current_url: Optional[str] = None

    # ------------------------
    # Public API
    # ------------------------
    def parse_content(self, url: str):
        self.logger.info(f"Processing url: {url}")
        self.current_url = url
        self.reload_handler.run(self)

    # ------------------------
    # Internal helpers
    # ------------------------
    def write_content(self):
        self.orchestra.run(self.current_url, self.get_soup(self.current_url))

    def _using_chrome(self) -> bool:
        return self.driver_handler is not None

    def get_soup(self, url: str) -> BeautifulSoup:
        if self._using_chrome():
            html = self.driver_handler.get_driver().page_source
        else:
            r = requests.get(url)
            try:
                html = r.content.decode("utf8")
            except Exception:
                html = r.text
        return BeautifulSoup(html, "html.parser")

    def _current_dom(self) -> BeautifulSoup:
        if self._using_chrome():
            return BeautifulSoup(self.driver_handler.get_driver().page_source, "html.parser")
        raise RuntimeError("_current_dom called without chrome driver")

    def handle_block_and_scroll(self, soup: BeautifulSoup):
        if not self._using_chrome():
            return
        # 1) Try to bypass blocking screens (input/click) using provided handler
        try:
            self.block_handler.handle(self.driver_handler.get_driver(), soup)
        except TargetNotFoundException as e:
            self.logger.warning(f"Block screen handler failed", exc_info=e)
            pass

        # After possible interactions, DOM likely changed
        soup = self._current_dom()

        # 2) Apply scrolling strategy (e.g., load dynamic content)
        self.scroll_strategy.handle(self.driver_handler.get_driver(), soup)
