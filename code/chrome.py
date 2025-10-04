import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from utils.web_functions import fill_standard_chrome_options
from settings import window_w, window_h, screen_w, screen_h, chrome_driver_path, process_dict_default as PrDD

def get_driver(chosen_dict: dict):
    chrome_dir = chosen_dict.get("chrome_dir", PrDD.get("chrome_dir"))
    chrome_profile = chosen_dict.get("chrome_profile", PrDD.get("chrome_profile"))

    if chosen_dict.get("chrome_undetected", PrDD.get("chrome_undetected")):
        driver = undetected(chrome_dir, chrome_profile)
    else:
        driver = usual(chrome_dir, chrome_profile)

    driver.set_window_position((screen_w - window_w) * 0.5, (screen_h - window_h) * 0.5)
    driver.set_window_size(window_w, window_h)

    return driver

def undetected(chrome_dir, chrome_profile):
    options = uc.ChromeOptions()
    fill_standard_chrome_options(options, chrome_dir, chrome_profile)
    return uc.Chrome(driver_executable_path=chrome_driver_path, options=options)

def usual(chrome_dir, chrome_profile):
    service = Service(chrome_driver_path)
    options = Options()
    fill_standard_chrome_options(options, chrome_dir, chrome_profile)
    return webdriver.Chrome(service=service, options=options)
