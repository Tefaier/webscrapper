from __future__ import annotations

import time
from typing import Optional, List
from urllib.parse import urljoin

from bs4 import BeautifulSoup, PageElement
from bs4.element import Tag

from objects.elements.elements_collector import ElementsCollector
from objects.types.custom_exceptions import (
    TargetNotFoundException,
    LinkException,
    NextChapterNotReachedException, UnsupportedArgumentsException,
)
from settings import MAX_WAIT_FOR_BUTTON_CLICK_CHANGE as DEFAULT_MAX_CLICK_WAIT

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
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
    - link_reload: after click, wait up to wait_for_click_change_seconds for URL to change; error if not changed
    - link_pure_click: after click, do not enforce URL change; simply return current driver URL

    Raises TargetNotFoundException if no link element found.
    Raises LinkException if click didn't result in URL change where expected.
    Raises NextChapterNotReachedException if navigation by URL/JS didn't change the URL.
    """

    def __init__(
        self,
        link_collector: ElementsCollector,
        driver: Optional[WebDriver] = None,
        press_link: bool = True,
        link_reload: bool = False,
        link_pure_click: bool = False,
        wait_for_click_change_seconds: float = DEFAULT_MAX_CLICK_WAIT,
    ) -> None:
        self.link_collector = link_collector
        self.driver: Optional[WebDriver] = driver
        self.press_link = press_link
        self.link_reload = link_reload
        self.link_pure_click = link_pure_click
        self.wait_for_click_change_seconds = wait_for_click_change_seconds

    def set_driver(self, driver: WebDriver) -> None:
        self.driver = driver

    # ------------------------
    # Public API
    # ------------------------
    def navigate(self, current_url: str, soup: BeautifulSoup) -> str:
        """Find next link using collector and perform navigation according to configuration.

        Returns the resolved next URL (absolute) or the driver's current URL after clicking.
        May return javascript:... URL if driver is not provided and link is javascript.
        """
        link_el = self._get_link_element(soup)

        if self.driver is None:
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
        if self.driver is None:
            raise RuntimeError("Click requested but selenium WebDriver or utilities not available")
        previous_url = self.driver.current_url

        # Find same element in the live DOM and click it
        xpath = xpath_soup(link_el)  # type: ignore[arg-type]
        web_el = self.driver.find_element(By.XPATH, xpath)
        self.driver.execute_script("arguments[0].click();", web_el)

        self._loop_driver_url_change(previous_url)

        if self.link_reload:
            if self.driver.current_url == previous_url:
                raise LinkException("Pressing located link didn't change url")
            self.driver.get(self.driver.current_url)
            return self.driver.current_url

        if self.link_pure_click:
            # No validation requested
            return self.driver.current_url

        if self.driver.current_url == previous_url:
            raise LinkException("Pressing located link didn't change url")

        return self.driver.current_url

    def _navigate_by_href(self, current_url: str, link_el: PageElement) -> str:
        if self.driver is None:
            raise RuntimeError("Driver is required for navigate-by-href mode")
        href = link_el.get("href") if hasattr(link_el, "get") else None
        if not href:
            raise LinkException("Link element has no href to navigate by")

        previous_url = self.driver.current_url

        if href.startswith("javascript"):
            # Execute inline JS and wait for navigation
            self.driver.execute_script(href)
            if not self._loop_driver_url_change(previous_url):
                raise NextChapterNotReachedException(f"javascript navigation didn't change url: {href}")

        next_abs = urljoin(current_url, href)
        if self.driver.current_url == next_abs:
            # Same URL target - force refresh
            self.driver.refresh()
            if not self._loop_driver_url_change(previous_url):
                raise NextChapterNotReachedException(f"Implemented refresh strategy for the same href: {next_abs} but url didn't change")
        else:
            self.driver.get(next_abs)

        if self.driver.current_url == previous_url:
            raise NextChapterNotReachedException("Navigation by href didn't change url")
        return self.driver.current_url

    """
    Loops checking whether url on driver changed. Returns whether url changed
    """
    def _loop_driver_url_change(self, previous_url: str) -> bool:
        deadline = time.time() + float(self.wait_for_click_change_seconds or 0)
        while time.time() < deadline:
            time.sleep(0.1)
            if self.driver.current_url != previous_url:
                return True
        return False
