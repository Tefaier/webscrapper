from __future__ import annotations

import time
from typing import List

from bs4 import BeautifulSoup
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from objects.file_handlers.log_writer import LogWriter
from objects.web_handlers.driver_handler import DriverHandler
from settings.web_handlers_defaults import CAPTCHA_WAIT, CAPTCHA_RETRY
from utils.web_functions import xpath_soup
from objects.types.custom_exceptions import TargetNotFoundException

from objects.elements.elements_finders import ElementsFinder
from objects.web_handlers.web_handler import WebHandler


class BlockScreenHandler(WebHandler):
    def __init__(self, log_writer: LogWriter):
        self.logger = log_writer.get_logger(type(self).__name__)


class NoHandling(BlockScreenHandler):
    def handle(self, driver: DriverHandler, soup: BeautifulSoup, attempt: int) -> None:
        pass


class CollectedHandler(BlockScreenHandler):
    def __init__(self, log_writer: LogWriter, sub_handlers: List[BlockScreenHandler]):
        super().__init__(log_writer)
        self.sub_handlers = sub_handlers

    def handle(self, driver: DriverHandler, soup: BeautifulSoup, attempt: int) -> None:
        for handle in self.sub_handlers:
            handle.handle(driver, soup, attempt)


class FieldInputHandler(BlockScreenHandler):
    def __init__(self, log_writer: LogWriter, input_finder: ElementsFinder, to_input: str):
        super().__init__(log_writer)
        self.input_finder = input_finder
        self.to_input = to_input

    def handle(self, driver: DriverHandler, soup: BeautifulSoup, attempt: int) -> None:
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

    def handle(self, driver: DriverHandler, soup: BeautifulSoup, attempt: int) -> None:
        located = self.button_finder.find(soup)
        if len(located) == 0:
            raise TargetNotFoundException("Failed to find button field with locator provided")
        xpath_to_input = xpath_soup(located[0])
        button_field = driver.find_element(By.XPATH, xpath_to_input)
        if button_field is not None:
            button_field.click()
        else:
            raise TargetNotFoundException(f"Failed to find button field with xpath {xpath_to_input}")


class CaptchaClickHandler(BlockScreenHandler):
    def __init__(self, log_writer: LogWriter, max_wait_time: float = CAPTCHA_WAIT, retry_time: float = CAPTCHA_RETRY):
        super().__init__(log_writer)
        self.max_wait_time = max_wait_time
        self.retry_time = retry_time

    def handle(self, driver: DriverHandler, soup: BeautifulSoup, attempt: int) -> None:
        if attempt == 1:
            return
        time.sleep(5)
        driver.try_solve_captcha()
        time.sleep(5)

        # for now unable to get captcha text
        if self._check_needs_click(driver):
            driver.try_solve_captcha()
        if self._check_needs_wait(driver):
            start_time = time.time()
            while time.time() < start_time + self.max_wait_time:
                time.sleep(self.retry_time)
                if self._check_needs_click(driver):
                    self.logger.info(f"Waited for captcha for {time.time() - start_time:.2f}s")
                    driver.try_solve_captcha()
                    return
            self.logger.warning("Failed to wait for captcha to become clickable")

    def _check_needs_wait(self, driver: DriverHandler) -> bool:
        content = self._get_captcha_text(driver)
        if "Verifying..." in content or "Идет проверка..." in content:
            return True
        return False

    def _check_needs_click(self, driver: DriverHandler) -> bool:
        content = self._get_captcha_text(driver)
        if "Verify you are a human" in content or "Подтвердите, что вы человек" in content:
            return True
        return False

    def _get_captcha_text(self, driver: DriverHandler) -> str:
        try:
            return (
                driver.unsafe_driver_get()
                .find_element("div.main_wrapper > div > div")
                .shadow_root.find_element("iframe")
                .text
            )
        except:
            pass
        return ""
