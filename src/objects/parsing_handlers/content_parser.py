from __future__ import annotations

from typing import Optional

import requests
from bs4 import BeautifulSoup
from objects.elements.elements_orchestra import ElementsOrchestra
from objects.file_handlers.log_writer import LogWriter
from objects.types.custom_exceptions import TargetNotFoundException
from objects.web_handlers.block_screen_handler import BlockScreenHandler
from objects.web_handlers.driver_handler import DriverHandler
from objects.web_handlers.scroll_strategy import ScrollStrategy
from objects.web_handlers.reload_handler import ReloadHandler
from settings.parsing_handlers_defaults import REQUEST_GET_TIMEOUT_SECONDS


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
        driver_handler: Optional[DriverHandler] = None,
    ) -> None:
        self.logger = log_writer.get_logger(type(self).__name__)
        self.orchestra = orchestra
        self.scroll_strategy: ScrollStrategy = scroll_strategy
        self.block_handler: BlockScreenHandler = block_handler
        self.reload_handler: ReloadHandler = reload_handler
        self.driver_handler = driver_handler
        self.current_url: Optional[str] = None
        self._last_request_url: Optional[str] = None
        self._last_request_content: Optional[str] = None

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
            html = self.driver_handler.get(url).get_content()
        else:
            if self._last_request_url == url and self._last_request_content:
                html = self._last_request_content
            else:
                try:
                    r = requests.get(url, timeout=REQUEST_GET_TIMEOUT_SECONDS)
                    try:
                        html = r.content.decode("utf8")
                    except Exception as e:
                        self.logger.warning("Failed while decoding request", e)
                        html = r.text
                except Exception as e:
                    self.logger.warning("Failed while making request", e)
                    html = ""
                self._last_request_url = url
                self._last_request_content = html
        return BeautifulSoup(html, "html.parser")

    def handle_block_and_scroll(self, soup: BeautifulSoup):
        if not self._using_chrome():
            return
        # 1) Try to bypass blocking screens (input/click) using provided handler
        try:
            self.block_handler.handle(self.driver_handler, soup)
        except TargetNotFoundException as e:
            self.logger.warning(f"Block screen handler failed", exc_info=e)
            pass

        # After possible interactions, DOM likely changed
        soup = BeautifulSoup(self.driver_handler.get_content(), "html.parser")

        # 2) Apply scrolling strategy (e.g., load dynamic content)
        self.scroll_strategy.handle(self.driver_handler, soup)

    def close(self):
        try:
            self.orchestra.output.close()
        except Exception as e:
            self.logger.error("Failed while closing output", exc_info=e)
        try:
            if self.driver_handler:
                self.driver_handler.quit()
        except Exception as e:
            self.logger.error("Failed while clearing driver", exc_info=e)
