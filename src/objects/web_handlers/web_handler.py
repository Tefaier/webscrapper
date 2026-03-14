from __future__ import annotations

from abc import ABC, abstractmethod

from bs4 import BeautifulSoup

from objects.web_handlers.driver_handler import DriverHandler


class WebHandler(ABC):
    @abstractmethod
    def handle(self, driver: DriverHandler, soup: BeautifulSoup, attempt: int) -> None: ...
