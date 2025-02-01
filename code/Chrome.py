import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from Settings import window_w, window_h, screen_w, screen_h, chrome_driver_path, process_dict_default as PrDD

def get_driver(chosen_dict: dict):
    chrome_dir = chosen_dict.get("chrome_dir", PrDD.get("chrome_dir"))
    chrome_profile = chosen_dict.get("chrome_profile", PrDD.get("chrome_profile"))

    if chrome_dir is not None and chrome_profile is not None and not chosen_dict.get("chrome_undetected", PrDD.get("chrome_undetected")):
        driver = usual(chrome_dir, chrome_profile)
    else:
        driver = undetected()

    driver.set_window_position((screen_w - window_w) * 0.5, (screen_h - window_h) * 0.5)
    driver.set_window_size(window_w, window_h)

    return driver

def undetected():
    options = uc.ChromeOptions()
    options.page_load_strategy = 'eager'
    return uc.Chrome(driver_executable_path=chrome_driver_path,
                     options=options)

def usual(chrome_dir, chrome_profile):
    service = Service(chrome_driver_path)
    options = Options()
    options.page_load_strategy = 'eager'
    options.add_argument("--user-data-dir=" + chrome_dir)
    options.add_argument("--profile-directory=" + chrome_profile)
    options.add_argument("--no-default-browser-check")
    options.add_argument("--no-first-run")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("disable-infobars")
    options.add_argument("--start-maximized")
    return webdriver.Chrome(service=service, options=options)
