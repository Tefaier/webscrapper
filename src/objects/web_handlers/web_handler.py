from __future__ import annotations

from abc import ABC, abstractmethod

from bs4 import BeautifulSoup
from selenium.webdriver.chrome.webdriver import WebDriver

class WebHandler(ABC):
    @abstractmethod
    def handle(self, driver: WebDriver, soup: BeautifulSoup) -> None: ...
