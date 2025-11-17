from __future__ import annotations

from typing import List

from bs4 import BeautifulSoup
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from objects.file_handlers.log_writer import LogWriter
from utils.web_functions import xpath_soup
from objects.types.custom_exceptions import TargetNotFoundException

from objects.elements.elements_finders import ElementsFinder
from objects.web_handlers.web_handler import WebHandler


class BlockScreenHandler(WebHandler):
    def __init__(self, log_writer: LogWriter):
        self.logger = log_writer.get_logger(type(self).__name__)


class NoHandling(BlockScreenHandler):
    def handle(self, driver: WebDriver, soup: BeautifulSoup) -> None:
        pass


class CollectedHandler(BlockScreenHandler):
    def __init__(self, log_writer: LogWriter, sub_handlers: List[BlockScreenHandler]):
        super().__init__(log_writer)
        self.sub_handlers = sub_handlers

    def handle(self, driver: WebDriver, soup: BeautifulSoup) -> None:
        for handle in self.sub_handlers:
            handle.handle(driver, soup)


class FieldInputHandler(BlockScreenHandler):
    def __init__(self, log_writer: LogWriter, input_finder: ElementsFinder, to_input: str):
        super().__init__(log_writer)
        self.input_finder = input_finder
        self.to_input = to_input

    def handle(self, driver: WebDriver, soup: BeautifulSoup) -> None:
        located = self.input_finder.find(soup)
        if len(located) == 0:
            raise TargetNotFoundException("Failed to find input field with locator provided")
        xpath_to_input = xpath_soup(located[0])
        input_field = driver.find_element(By.XPATH, xpath_to_input)
        if input_field is not None:
            input_field.send_keys(self.to_input)
        else:
            raise TargetNotFoundException(f"Failed to find input field with xpath {xpath_to_input}")


class ButtonClickHandler(BlockScreenHandler):
    def __init__(self, log_writer: LogWriter, button_finder: ElementsFinder):
        super().__init__(log_writer)
        self.button_finder = button_finder

    def handle(self, driver: WebDriver, soup: BeautifulSoup) -> None:
        located = self.button_finder.find(soup)
        if len(located) == 0:
            raise TargetNotFoundException("Failed to find button field with locator provided")
        xpath_to_input = xpath_soup(located[0])
        button_field = driver.find_element(By.XPATH, xpath_to_input)
        if button_field is not None:
            button_field.click()
        else:
            raise TargetNotFoundException(f"Failed to find button field with xpath {xpath_to_input}")
