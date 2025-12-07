import base64
import re
from typing import Optional, Dict, List

import cssutils
import cv2
import numpy as np
from bs4 import BeautifulSoup, PageElement, Tag, NavigableString
from pytesseract import pytesseract
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By


# from https://gist.github.com/ergoithz/6cf043e3fdedd1b94fcf
def xpath_soup(element: PageElement) -> str:
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:
        siblings = parent.find_all(child.name, recursive=False)
        components.append(
            child.name
            if 1 == len(siblings)
            else "%s[%d]" % (child.name, next(i for i, s in enumerate(siblings, 1) if s is child))
        )
        child = parent
    components.reverse()
    return "/%s" % "/".join(components)


def unwrap_xpath(driver: WebDriver, xpath):
    parts = xpath.split("/")
    current_path = parts[0]
    for part in parts[1:]:
        current_path += "/" + part
        # unwrap details
        if part.count("details") == 1:
            obj = driver.find_element(By.XPATH, current_path)
            driver.execute_script("arguments[0].open = true;", obj)


def extract_all_styles(soup: BeautifulSoup) -> Dict[str, Dict[str, str]]:
    css_classes = {}
    for styles in soup.select("style"):
        try:
            css = cssutils.parseString(styles.encode_contents(), validate=False)
        except Exception as e:
            continue
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
                if ("." + css_class) not in css_classes_info:
                    continue
                for k, v in css_classes_info["." + css_class].items():
                    parsed_styles[k] = v
        return not (
            parsed_styles.get("overflow", "Yes") == "hidden"
            or parsed_styles.get("display", "Yes") == "none"
            or element.get("display", "Yes") == "none"
        )
    return True


def take_element_viewed_content(driver: WebDriver, expected_language: List[str], element: PageElement) -> str:
    xpath = xpath_soup(element)
    unwrap_xpath(driver, xpath)
    obj = driver.find_element(By.XPATH, xpath)
    driver.execute_script("arguments[0].scrollIntoView(true);", obj)

    image_data = base64.b64decode(obj.screenshot_as_base64)
    # image_data = get_screen_of_element(driver, obj, 5, 5)
    img = cv2.imdecode(np.asarray(bytearray(image_data), dtype=np.uint8), cv2.IMREAD_COLOR)
    result = pytesseract.image_to_string(img, lang=expected_language)
    return result


def replace_element_with_text(soup: BeautifulSoup, element: PageElement, text: str) -> PageElement:
    if isinstance(element, Tag):
        replacement = soup.new_tag("p")
        replacement.string = text
        element.replace_with(replacement)
        replacement.sourceline = element.sourceline
        replacement.sourcepos = element.sourcepos
        return replacement
    else:
        return NavigableString(text)


def get_domain(url: str) -> Optional[str]:
    domain = re.search(r"https?://([^/]+)", url)
    if domain:
        return domain.group(1)
    return None
