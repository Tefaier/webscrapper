from typing import Dict

from selenium.webdriver.chrome.webdriver import WebDriver
from seleniumbase import Driver

from settings.system_defaults import *
from settings.web_handlers_defaults import *


class DriverHandler:
    def __init__(
        self,
        chrome_directory: str = CHROME_DIRECTORY,
        chrome_undetected_directory: str = CHROME_UNDETECTED_DIRECTORY,
        undetected_method: bool = UNDETECTED_METHOD,
        window_width: int = WINDOW_WIDTH,
        window_height: int = WINDOW_HEIGHT,
    ):
        self.chrome_directory = chrome_directory
        self.chrome_undetected_directory = chrome_undetected_directory
        self.undetected = undetected_method
        self.window_width = min(WINDOW_W_MAX, max(WINDOW_W_MIN, window_width))
        self.window_height = min(WINDOW_H_MAX, max(WINDOW_H_MIN, window_height))
        self.driver = self._create_driver()

    def get_driver(self) -> WebDriver:
        return self.driver

    def recreate_driver(self) -> WebDriver:
        self.driver.quit()
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
        return Driver(
            uc=True,
            headless=True,
            user_data_dir=self.chrome_undetected_directory or "/tmp/.google_chrome_undetected",
            **self._build_default_settings()
        )

    def _usual(self) -> WebDriver:
        return Driver(
            uc=False,
            headless=True,
            user_data_dir=self.chrome_directory or "/tmp/.google_chrome",
            **self._build_default_settings()
        )

    def _build_default_settings(self) -> Dict[str, str]:
        return {
            "browser": "chrome",
            "use_auto_ext": False,
            "disable_features": "LensOverlay,TranslateUI,Translate,OptimizationGuideModelDownloading,OptimizationHintsFetching,OptimizationTargetPrediction,OptimizationHints",
            "page_load_strategy": "eager",
            "locale_code": "en",
            "d_width": self.window_width,
            "d_height": self.window_height,
            "chromium_arg": "--no-sandbox,--disable-dev-shm-usage",
        }
