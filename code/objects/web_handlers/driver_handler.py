import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver

from settings.system_defaults import *
from settings.web_handlers_defaults import *
from utils.web_functions import fill_standard_chrome_options


class DriverHandler:
    def __init__(
            self,
            chrome_directory: str = CHROME_DIRECTORY,
            chrome_profile: str = CHROME_PROFILE,
            undetected_method: bool = UNDETECTED_METHOD,
            window_width: int = WINDOW_WIDTH,
            window_height: int = WINDOW_HEIGHT
    ):
        self.chrome_directory = chrome_directory
        self.chrome_profile = chrome_profile
        self.undetected = undetected_method
        self.window_width = min(WINDOW_W_MAX, max(WINDOW_W_MIN, window_width))
        self.window_height = min(WINDOW_H_MAX, max(WINDOW_H_MIN, window_height))
        self.driver = self._create_driver()

    def get_driver(self) -> WebDriver:
        return self.driver

    def recreate_driver(self) -> WebDriver:
        self.driver.close()
        self.driver = self._create_driver()
        return self.driver

    def _create_driver(self) -> WebDriver:
        if self.undetected:
            driver = self._undetected()
        else:
            driver = self._usual()

        driver.set_window_size(self.window_width, self.window_height)

        return driver

    def _undetected(self) -> WebDriver:
        options = uc.ChromeOptions()
        fill_standard_chrome_options(options, self.chrome_directory, self.chrome_profile)
        return uc.Chrome(driver_executable_path=CHROME_DRIVER_PATH, options=options)

    def _usual(self) -> WebDriver:
        service = Service(CHROME_DRIVER_PATH)
        options = Options()
        fill_standard_chrome_options(options, self.chrome_directory, self.chrome_profile)
        return webdriver.Chrome(service=service, options=options)
