from abc import ABC, abstractmethod
from typing import Dict, Optional, Union

from selenium.webdriver.common.by import By
from seleniumbase.undetected import WebElement
from seleniumbase.undetected.cdp_driver.element import Element
from typing_extensions import Self

from seleniumbase import Driver, BaseCase, SB
from seleniumbase.core.browser_launcher import uc_open_with_reconnect, uc_open, uc_gui_click_captcha
from seleniumbase.core.sb_driver import DriverMethods
from typing_extensions import override

from objects.types.driver_types import DriverTypes
from settings.system_defaults import *
from settings.web_handlers_defaults import *


class DriverHandler(ABC):
    def __new__(cls, type: DriverTypes, *args, **kwargs):
        if type == DriverTypes.Regular:
            return super().__new__(RegularDriverHandler)
        elif type == DriverTypes.Undetected:
            return super().__new__(UndetectedDriverHandler)
        elif type == DriverTypes.CDP:
            return super().__new__(CdpDriverHandler)
        else:
            return super().__new__(cls)

    def __init__(
        self,
        type: DriverTypes = DriverTypes.Regular,
        chrome_directory: str = CHROME_DIRECTORY,
        chrome_undetected_directory: str = CHROME_UNDETECTED_DIRECTORY,
        window_width: int = WINDOW_WIDTH,
        window_height: int = WINDOW_HEIGHT,
    ):
        self.type = type
        self.chrome_directory = chrome_directory
        self.chrome_undetected_directory = chrome_undetected_directory
        self.window_width = min(WINDOW_W_MAX, max(WINDOW_W_MIN, window_width))
        self.window_height = min(WINDOW_H_MAX, max(WINDOW_H_MIN, window_height))
        self.driver = self._create_driver()
        self.first_open = True

    @abstractmethod
    def _create_driver(self) -> DriverMethods:
        """Creates driver that will be stored in self.driver"""
        pass

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

    def get_url(self) -> str:
        return self.driver.get_current_url()

    def execute(self, script: str, *args) -> Self:
        self.driver.execute_script(script, *args)
        return self

    @abstractmethod
    def get(self, url: str) -> Self:
        pass

    def get_content(self) -> str:
        return self.driver.get_page_source()

    def reload(self) -> Self:
        self.driver.refresh()
        return self

    @abstractmethod
    def clear_story(self) -> Self:
        pass

    def recreate(self) -> Self:
        self.quit()
        self.driver = self._create_driver()
        self.first_open = True
        return self

    @abstractmethod
    def quit(self) -> Self:
        pass

    def find_element(self, by: str, cond: Optional[str]) -> Union[WebElement, Element]:
        return self.driver.find_element(by, cond)

    def unsafe_driver_get(self):
        return self.driver

    def scroll(self) -> Self:
        self.execute("window.scrollTo(0, document.body.scrollHeight);")
        return self


class RegularDriverHandler(DriverHandler):
    def __init__(
        self,
        type: DriverTypes = DriverTypes.Regular,
        chrome_directory: str = CHROME_DIRECTORY,
        chrome_undetected_directory: str = CHROME_UNDETECTED_DIRECTORY,
        window_width: int = WINDOW_WIDTH,
        window_height: int = WINDOW_HEIGHT,
    ):
        super().__init__(type, chrome_directory, chrome_undetected_directory, window_width, window_height)

    @override
    def _create_driver(self) -> DriverMethods:
        driver = Driver(
            uc=False,
            headless=True,
            user_data_dir=self.chrome_directory or "/tmp/.google_chrome",
            **self._build_default_settings(),
        )
        driver.set_window_size(self.window_width, self.window_height)
        return driver

    @override
    def get(self, url: str) -> Self:
        self.first_open = False
        if self.driver.current_url == url:
            return self
        self.driver.get(url)
        return self

    @override
    def clear_story(self) -> Self:
        self.driver.delete_all_cookies()
        return self

    @override
    def quit(self) -> Self:
        self.driver.quit()
        return self


class UndetectedDriverHandler(DriverHandler):
    def __init__(
        self,
        type: DriverTypes = DriverTypes.Regular,
        chrome_directory: str = CHROME_DIRECTORY,
        chrome_undetected_directory: str = CHROME_UNDETECTED_DIRECTORY,
        window_width: int = WINDOW_WIDTH,
        window_height: int = WINDOW_HEIGHT,
    ):
        super().__init__(type, chrome_directory, chrome_undetected_directory, window_width, window_height)

    @override
    def _create_driver(self) -> DriverMethods:
        driver = Driver(
            uc=True,
            headless=True,
            incognito=True,
            user_data_dir=self.chrome_undetected_directory or "/tmp/.google_chrome_undetected",
            **self._build_default_settings(),
        )
        driver.set_window_size(self.window_width, self.window_height)
        return driver

    @override
    def get(self, url: str) -> Self:
        if self.driver.current_url == url:
            return self
        if self.first_open:
            uc_open_with_reconnect(self.driver, url)
            uc_gui_click_captcha(self.driver)
        else:
            uc_open(self.driver, url)
        self.first_open = False
        return self

    @override
    def clear_story(self) -> Self:
        self.driver.delete_all_cookies()
        return self

    @override
    def quit(self) -> Self:
        self.driver.quit()
        return self


class CdpDriverHandler(DriverHandler):
    def __init__(
        self,
        type: DriverTypes = DriverTypes.Regular,
        chrome_directory: str = CHROME_DIRECTORY,
        chrome_undetected_directory: str = CHROME_UNDETECTED_DIRECTORY,
        window_width: int = WINDOW_WIDTH,
        window_height: int = WINDOW_HEIGHT,
    ):
        super().__init__(type, chrome_directory, chrome_undetected_directory, window_width, window_height)

    @override
    def _create_driver(self) -> DriverMethods:
        driver = Driver(
            uc=True,
            headless=True,
            incognito=True,
            user_data_dir=self.chrome_undetected_directory or "/tmp/.google_chrome_undetected",
            **self._build_default_settings(),
        )
        driver.set_window_size(self.window_width, self.window_height)
        return driver

    @override
    def get(self, url: str) -> Self:
        if self.driver.get_current_url() == url:
            return self
        if self.first_open:
            self.driver.activate_cdp_mode(url)
            self.driver.uc_gui_click_captcha()
        else:
            self.driver.cdp.open(url)
        self.first_open = False
        return self

    @override
    def clear_story(self) -> Self:
        self.driver.delete_all_cookies()
        self.driver.clear_local_storage()
        self.driver.clear_session_storage()
        return self

    @override
    def find_element(self, by: str, cond: Optional[str]) -> Union[WebElement, Element]:
        if by == By.XPATH:
            return self.driver.cdp.find_element(cond)
        else:
            raise Exception(f"Unsupported by: {by}")

    @override
    def quit(self) -> Self:
        self.driver.connect()
        self.driver.quit()
        return self
