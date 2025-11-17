from __future__ import annotations

import time
from typing import TYPE_CHECKING

from objects.file_handlers.log_writer import LogWriter
from objects.types.custom_exceptions import TargetNotFoundException, MaxOpeningTimeExceededException
from objects.web_handlers.driver_handler import DriverHandler
from settings.web_handlers_defaults import *


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
        log_writer: LogWriter,
        driver_handler: DriverHandler = None,
        sleep_before_open: bool = SLEEP_BEFORE_OPEN,
        sleep_before_open_seconds: float = SLEEP_BEFORE_OPEN_SECONDS,
        sleep_before_process: bool = SLEEP_BEFORE_PROCESS,
        sleep_before_process_seconds: float = SLEEP_BEFORE_PROCESS_SECONDS,
        max_attempts: int = MAX_ATTEMPTS,
        max_page_load_wait_seconds: float = MAX_PAGE_LOAD_WAIT_SECONDS,
        page_load_check_interval_seconds: float = PAGE_LOAD_CHECK_INTERVAL_SECONDS,
    ) -> None:
        self.logger = log_writer.get_logger(type(self).__name__)
        self.driver_handler = driver_handler
        self.sleep_before_open = sleep_before_open
        self.sleep_before_open_seconds = sleep_before_open_seconds
        self.wait_before_process = sleep_before_process
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
        if self.sleep_before_open and self.sleep_before_open_seconds > 0.0:
            time.sleep(self.sleep_before_open_seconds)

        while attempts <= self.max_attempts:
            attempts += 1
            self.logger.info(f"Attempt {attempts}")
            if self._attempt_once(parser):
                return
            if self.driver_handler and self.max_page_load_wait_seconds > 0.0:
                deadline = time.time() + float(self.max_page_load_wait_seconds)
                while time.time() < deadline:
                    time.sleep(self.page_load_check_interval_seconds)
                    try:
                        soup = parser.get_soup(parser.current_url)
                        parser.handle_block_and_scroll(soup)
                        parser.write_content()
                        return
                    except TargetNotFoundException:
                        pass
            self._perform_refresh(parser, attempts)

        self.logger.warning(f"Number of attempts exceeded limit, failed")
        raise MaxOpeningTimeExceededException("Seemed to fail overcoming defence")

    # ------------------------
    # Internal helpers
    # ------------------------
    def _attempt_once(self, parser: ContentParser) -> bool:
        """Single attempt to open/process the page. Returns whether operation succeeded"""
        soup = parser.get_soup(parser.current_url)
        if self.driver_handler:
            parser.handle_block_and_scroll(soup)
            self._maybe_wait_before_process()

        try:
            parser.write_content()
            return True
        except TargetNotFoundException as e:
            self.logger.warning("Writing content failed", exc_info=e)
            return False

    def _maybe_wait_before_process(self) -> None:
        if self.wait_before_process and self.sleep_before_process_seconds > 0:
            time.sleep(self.sleep_before_process_seconds)

    def _perform_refresh(self, parser: ContentParser, attempt: int):
        if self.driver_handler is None:
            return
        if attempt < self.max_attempts:
            self.logger.debug("Deleting cookies and refresh")
            self.driver_handler.get_driver().delete_all_cookies()
            self.driver_handler.get_driver().refresh()
        else:
            self.logger.debug("Creating new session")
            self.driver_handler.recreate_driver().get(parser.current_url)
