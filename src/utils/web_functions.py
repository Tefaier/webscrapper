import base64
import io
import re
from typing import Optional, Union, Dict, List

import cssutils
import cv2
import numpy as np
from bs4 import BeautifulSoup, PageElement, Tag, NavigableString
from pytesseract import pytesseract
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from undetected_chromedriver import ChromeOptions
from PIL import Image

# from https://gist.github.com/ergoithz/6cf043e3fdedd1b94fcf
def xpath_soup(element: PageElement) -> str:
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:
        siblings = parent.find_all(child.name, recursive=False)
        components.append(
            child.name if 1 == len(siblings) else '%s[%d]' % (
                child.name,
                next(i for i, s in enumerate(siblings, 1) if s is child)
            )
        )
        child = parent
    components.reverse()
    return '/%s' % '/'.join(components)

def unwrap_xpath(driver: WebDriver, xpath):
    parts = xpath.split('/')
    current_path = parts[0]
    for part in parts[1:]:
        current_path += '/' + part
        # unwrap details
        if part.count('details') == 1:
            obj = driver.find_element(By.XPATH, current_path)
            driver.execute_script("arguments[0].open = true;", obj)

def fill_standard_chrome_options(options: Union[Options, ChromeOptions], chrome_dir, chrome_profile):
    options.page_load_strategy = 'eager'
    options.add_argument("--headless=new")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--no-first-run")
    options.add_argument("--no-sandbox")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-translate")
    options.add_argument("--start-maximized")
    options.add_argument("--lang=en-US")
    options.add_argument(
        "--disable-features="
            "LensOverlay,"
            "TranslateUI,"
            "Translate,"
            "OptimizationGuideModelDownloading,"
            "OptimizationHintsFetching,"
            "OptimizationTargetPrediction,"
            "OptimizationHints"
    )
    if chrome_dir is not None:
        options.add_argument(f"--user-data-dir={chrome_dir}")
    if chrome_profile is not None:
        options.add_argument(f"--profile-directory={chrome_profile}")

def extract_all_styles(soup: BeautifulSoup) -> Dict[str, Dict[str, str]]:
    css_classes = {}
    for styles in soup.select('style'):
        css = cssutils.parseString(styles.encode_contents(), validate=False)
        for rule in css:
            if rule.type == rule.STYLE_RULE:
                style = rule.selectorText
                css_classes[style] = {}
                for item in rule.style:
                    css_classes[style][item.name] = item.value
    return css_classes

def check_element_visibility(css_classes_info: Dict[str, Dict[str, str]], element: PageElement) -> bool:
    if isinstance(element, Tag):
        style_name = "style"
        class_name = "class"
        attributes = dict(element.attrs)
        parsed_styles = {}
        if style_name in attributes.keys():
            s = cssutils.parseStyle(attributes[style_name])
            attributes.pop(style_name)
            parsed_styles.update(s)
        if class_name in attributes.keys():
            for css_class in attributes[class_name]:
                if ('.' + css_class) not in css_classes_info: continue
                for k, v in css_classes_info['.' + css_class].items():
                    parsed_styles[k] = v
        return not (parsed_styles.get("overflow", "Yes") == "hidden" or
                    parsed_styles.get("display", "Yes") == "none" or
                    element.get("display", "Yes") == "none")
    return True

def take_element_viewed_content(driver: WebDriver, expected_language: List[str], element: PageElement) -> str:
    xpath = xpath_soup(element)
    unwrap_xpath(driver, xpath)
    obj = driver.find_element(By.XPATH, xpath)
    driver.execute_script("arguments[0].scrollIntoView(true);", obj)

    image_data = base64.b64decode(obj.screenshot_as_base64)
    #image_data = get_screen_of_element(driver, obj, 5, 5)
    img = cv2.imdecode(np.asarray(bytearray(image_data), dtype=np.uint8), cv2.IMREAD_COLOR)
    result = pytesseract.image_to_string(img, lang=expected_language)
    return result

def get_screen_of_element(driver: WebDriver, element: WebElement, offset_x: int, offset_y: int) -> bytes:
    normalise = lambda val, hor, limits: min(max(val, limits[0][0] if hor else limits[0][1]),
                                             limits[1][0] if hor else limits[1][1])
    l = element.location_once_scrolled_into_view
    s = element.size
    limits = []
    limits.append([0, 0])
    limits.append([driver.get_window_size().get('width'), driver.get_window_size().get('height')])
    tup = (
        normalise(l['x'] - offset_x, True, limits),
        normalise(l['y'] - offset_y, False, limits),
        normalise(l['x'] + s['width'] + offset_x, True, limits),
        normalise(l['y'] + s['height'] + offset_y, False, limits),
    )

    screen_image = base64.b64decode(driver.get_screenshot_as_base64())
    image = Image.open(io.BytesIO(screen_image))
    # TODO check if it is still needed
    scale = image.size[0] / limits[1][0]  # shows scale of image relative to screen by width (should be the same by height)
    tup = tuple(int(scale * elem) for elem in tup)
    image = image.crop(tup)
    # image.show()  # comment later
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()

def replace_element_with_text(soup: BeautifulSoup, element: PageElement, text: str) -> PageElement:
        if isinstance(element, Tag):
            replacement = soup.new_tag('p')
            replacement.string = text
            element.replace_with(replacement)
            return replacement
        else:
            return NavigableString(text)
        
def get_domain(url: str) -> Optional[str]:
    domain = re.search(r'https?://([^/]+)', url)
    if domain:
        return domain.group(1)
    return None
