from __future__ import annotations

import time
from typing import Optional, List
from urllib.parse import urljoin

from bs4 import BeautifulSoup, PageElement
from bs4.element import Tag

from objects.elements.elements_collector import ElementsCollector
from objects.file_handlers.log_writer import LogWriter
from objects.types.custom_exceptions import (
    TargetNotFoundException,
    LinkException,
    NextChapterNotReachedException,
    UnsupportedArgumentsException,
)

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from objects.web_handlers.driver_handler import DriverHandler
from settings.web_handlers_defaults import *
from utils.web_functions import xpath_soup


class LinkHandler:
    """
    Handles navigation to the next page based on link elements found via ElementsCollector.

    Behavior:
    - Uses provided ElementsCollector to locate the link element in the current soup.
    - If no Selenium WebDriver is provided, returns an absolute URL derived from element href.
    - If a WebDriver is provided:
        - If press_link is True: tries to click the element and validates URL changed depending on flags.
        - If press_link is False: navigates via href (driver.get or executing javascript) and validates URL changed.

    Options mirror old_flow Parser behavior:
    - press_link: whether to click the element or navigate by href
    - link_reload: after click, force reload of new url no matter what
    - link_pure_click: after click, do not enforce URL change; simply return current driver URL

    Raises TargetNotFoundException if no link element found.
    Raises LinkException if click didn't result in URL change where expected.
    Raises NextChapterNotReachedException if navigation by URL/JS didn't change the URL.
    """

    def __init__(
        self,
        log_writer: LogWriter,
        link_collector: ElementsCollector,
        driver_handler: DriverHandler = None,
        press_link: bool = PRESS_LINK,
        reload_after: bool = RELOAD_AFTER,
        link_pure_click: bool = LINK_PURE_CLICK,
        wait_for_url_change_seconds: float = WAIT_FOR_URL_CHANGE_SECONDS,
    ) -> None:
        self.logger = log_writer.get_logger(type(self).__name__)
        self.link_collector = link_collector
        self.driver_handler = driver_handler
        self.press_link = press_link
        self.reload_after = reload_after
        self.link_pure_click = link_pure_click
        self.wait_for_url_change_seconds = wait_for_url_change_seconds

    # ------------------------
    # Public API
    # ------------------------
    def navigate(self, current_url: str, soup: BeautifulSoup) -> str:
        """Find next link using collector and perform navigation according to configuration.

        Returns the resolved next URL (absolute) or the driver's current URL after clicking.
        May return javascript:... URL if driver is not provided and link is javascript.
        """
        link_el = self._get_link_element(soup)

        if self.driver_handler is None:
            return self._resolve_url_without_driver(current_url, link_el)

        if self.press_link:
            return self._click_and_resolve(current_url, link_el)
        else:
            return self._navigate_by_href(current_url, link_el)

    # ------------------------
    # Internal helpers
    # ------------------------
    def _get_link_element(self, soup: BeautifulSoup) -> PageElement:
        candidates: List[PageElement] = self.link_collector.collect(soup) or []
        if len(candidates) == 0:
            raise TargetNotFoundException("No link candidates found by collector")
        return candidates[0]

    def _resolve_url_without_driver(self, current_url: str, link_el: PageElement) -> Optional[str]:
        href = link_el.get("href") if hasattr(link_el, "get") else None
        if not href:
            raise TargetNotFoundException("Link element has no href to resolve")
        if href.startswith("javascript"):
            raise UnsupportedArgumentsException("Tried to use link with javascript href without chrome being used")
        return urljoin(current_url, href)

    def _click_and_resolve(self, current_url: str, link_el: PageElement) -> str:
        if self.driver_handler is None:
            raise RuntimeError("Click requested but selenium WebDriver or utilities not available")
        previous_url = self.driver_handler.get_driver().current_url

        # Find same element in the live DOM and click it
        xpath = xpath_soup(link_el)  # type: ignore[arg-type]
        web_el = self.driver_handler.get_driver().find_element(By.XPATH, xpath)
        self.driver_handler.get_driver().execute_script("arguments[0].click();", web_el)

        self._loop_driver_url_change(previous_url)

        if self.reload_after:
            if self.driver_handler.get_driver().current_url == previous_url:
                raise LinkException("Pressing located link didn't change url")
            self.driver_handler.get_driver().get(self.driver_handler.get_driver().current_url)
            return self.driver_handler.get_driver().current_url

        if self.link_pure_click:
            # No validation requested
            return self.driver_handler.get_driver().current_url

        if self.driver_handler.get_driver().current_url == previous_url:
            raise LinkException("Pressing located link didn't change url")

        return self.driver_handler.get_driver().current_url

    def _navigate_by_href(self, current_url: str, link_el: PageElement) -> str:
        if self.driver_handler is None:
            raise RuntimeError("Driver is required for navigate-by-href mode")
        href = link_el.get("href") if hasattr(link_el, "get") else None
        if not href:
            raise LinkException("Link element has no href to navigate by")

        previous_url = self.driver_handler.get_driver().current_url

        if href.startswith("javascript"):
            # Execute inline JS and wait for navigation
            self.driver_handler.get_driver().execute_script(href)
            if not self._loop_driver_url_change(previous_url):
                raise NextChapterNotReachedException(f"javascript navigation didn't change url: {href}")

        next_abs = urljoin(current_url, href)
        if self.driver_handler.get_driver().current_url == next_abs:
            # Same URL target - force refresh
            self.driver_handler.get_driver().refresh()
            if not self._loop_driver_url_change(previous_url):
                raise NextChapterNotReachedException(
                    f"Implemented refresh strategy for the same href: {next_abs} but url didn't change"
                )
        else:
            self.driver_handler.get_driver().get(next_abs)

        if self.driver_handler.get_driver().current_url == previous_url:
            raise NextChapterNotReachedException("Navigation by href didn't change url")
        return self.driver_handler.get_driver().current_url

    """
    Loops checking whether url on driver changed. Returns whether url changed
    """

    def _loop_driver_url_change(self, previous_url: str) -> bool:
        deadline = time.time() + float(self.wait_for_url_change_seconds or 0)
        while time.time() < deadline:
            time.sleep(0.1)
            if self.driver_handler.get_driver().current_url != previous_url:
                return True
        return False
