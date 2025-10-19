import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from utils.web_functions import fill_standard_chrome_options
from settings import chrome_driver_path


class DriverHandler:
    def __init__(self, chrome_directory: str, chrome_profile: str, undetected_method: bool):
        self.chrome_directory = chrome_directory
        self.chrome_profile = chrome_profile
        self.undetected = undetected_method

    def create_driver(self):
        if self.undetected:
            driver = self._undetected()
        else:
            driver = self._usual()

        # driver.set_window_position((screen_w - window_w) * 0.5, (screen_h - window_h) * 0.5)
        # driver.set_window_size(window_w, window_h)

        return driver

    def _undetected(self):
        options = uc.ChromeOptions()
        fill_standard_chrome_options(options, self.chrome_directory, self.chrome_profile)
        return uc.Chrome(driver_executable_path=chrome_driver_path, options=options)

    def _usual(self):
        service = Service(chrome_driver_path)
        options = Options()
        fill_standard_chrome_options(options, self.chrome_directory, self.chrome_profile)
        return webdriver.Chrome(service=service, options=options)
