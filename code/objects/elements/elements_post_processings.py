from typing import List

from bs4 import BeautifulSoup, NavigableString, Tag, PageElement
from selenium.webdriver.chrome.webdriver import WebDriver

from objects.elements.elements_collector import ElementsCollector
from objects.types.custom_exceptions import UnsupportedArgumentsException
from utils.web_functions import extract_all_styles, check_element_visibility, take_element_viewed_content


class ElementsPostProcessing:
    def process(self, soup: BeautifulSoup, elements: List[PageElement]) -> List[PageElement]: ...


class SidesCutFiltering(ElementsPostProcessing):
    def __init__(self, cut_from_beginning: int = 0, cut_from_ending: int = 0):
        self.from_begin: int = max(0, cut_from_beginning)
        self.from_end: int = max(0, cut_from_ending)

    def process(self, soup: BeautifulSoup, elements: List[PageElement]) -> List[PageElement]:
        if len(elements) >= self.from_begin + self.from_end:
            return elements[self.from_begin:-self.from_end]
        raise UnsupportedArgumentsException(f"Wanted to have at least {self.from_begin + self.from_end} elements for cutting but actual count was {len(elements)}")


class ExactElementTaker(ElementsPostProcessing):
    def __init__(self, take_at_index: int = 0):
        self.index: int = max(0, take_at_index)

    def process(self, soup: BeautifulSoup, elements: List[PageElement]) -> List[PageElement]:
        if len(elements) > self.index:
            return [elements[self.index]]
        raise UnsupportedArgumentsException(f"Wanted to have at least {self.index + 1} elements for taking exact but actual count was {len(elements)}")


class VisibilityFilter(ElementsPostProcessing):
    def __init__(self):
        self.css_classes_info = {}

    def process(self, soup: BeautifulSoup, elements: List[PageElement]) -> List[PageElement]:
        self.css_classes_info = extract_all_styles(soup)
        elements = [element for element in elements if check_element_visibility( self.css_classes_info, element)]
        for element in elements:
            self.recursively_check(element)
        return elements

    def recursively_check(self, element: PageElement):
        if isinstance(element, Tag):
            for child in element.contents:
                if not check_element_visibility(self.css_classes_info, child):
                    child.extract()
                    continue
                self.recursively_check(child)


class JammedTextConverter(ElementsPostProcessing):
    def __init__(self, driver: WebDriver = None, expected_languages: List[str] = None, jammed_classes: List[str] = None, try_fix_text: bool = True):
        self.driver = driver
        self.expected_languages = expected_languages if expected_languages is not None else ["eng"]
        self.jammed_classes = jammed_classes if jammed_classes is not None else ["jum", "jmbl"]
        self.fix = try_fix_text

    def process(self, soup: BeautifulSoup, elements: List[PageElement]) -> List[PageElement]:
        if self.driver is None:
            return elements
        return [NavigableString(take_element_viewed_content(self.driver, self.expected_languages, element)) if self.check_element_is_jammed(element) else element for element in elements]

    def check_element_is_jammed(self, element: PageElement):
        if isinstance(element, Tag):
            return element.find('img') is not None or self.recursive_attr_check(element)
        return False

    def recursive_attr_check(self, element: PageElement):
        if isinstance(element, Tag):
            if element.has_attr("class") and any(jammed_class in element["class"] for jammed_class in self.jammed_classes):
                return True
            return any(self.recursive_attr_check(child) for child in element.contents)
        return False


class SubtreeRemovalFilter(ElementsPostProcessing):
    def process(self, soup: BeautifulSoup, elements: List[PageElement]) -> List[PageElement]:
        if not elements:
            return elements
        # Use ids because BeautifulSoup elements are not hashable
        element_ids = {id(e) for e in elements}
        filtered: List[PageElement] = []
        for e in elements:
            parent = getattr(e, "parent", None)
            is_nested = False
            while parent is not None:
                if id(parent) in element_ids:
                    is_nested = True
                    break
                parent = getattr(parent, "parent", None)
            if not is_nested:
                filtered.append(e)
        return filtered


class ExcludeByFinderFilter(ElementsPostProcessing):
    """
    Uses a provided ElementsFinder to find elements in the soup and excludes them from the given list.
    Only elements present in both the input list and the collector's results are removed.
    """

    def __init__(self, collector: ElementsCollector):
        self.collector = collector

    def process(self, soup: BeautifulSoup, elements: List[PageElement]) -> List[PageElement]:
        to_exclude = self.collector.collect(soup)
        if not to_exclude:
            return elements
        exclude_ids = {id(e) for e in to_exclude}
        return [e for e in elements if id(e) not in exclude_ids]


class SplitTagContentByInnerTags(ElementsPostProcessing):
    """
    For Tag elements, splits their textual content by occurrences of inner tags whose names are provided.
    Replaces such Tag elements with multiple NavigableStrings (including empty segments when separators are consecutive).
    Non-Tag elements are left untouched. If no splitter tag found inside a Tag, the element is kept as-is.
    """

    def __init__(self, split_tag_names: List[str]):
        self.split_names = {name.lower() for name in split_tag_names}

    def process(self, soup: BeautifulSoup, elements: List[PageElement]) -> List[PageElement]:
        result: List[PageElement] = []
        for el in elements:
            if isinstance(el, Tag):
                parts = self._split_text_by_tags(el)
                if parts is None:
                    result.append(el)
                else:
                    result.extend(NavigableString(p) for p in parts)
            else:
                result.append(el)
        return result

    def _split_text_by_tags(self, element: Tag):
        parts: List[str] = []
        buffer: List[str] = []
        had_splitter = False

        def walk(node: PageElement):
            nonlocal had_splitter
            if isinstance(node, NavigableString):
                buffer.append(str(node))
                return
            if isinstance(node, Tag):
                if node.name and node.name.lower() in self.split_names:
                    parts.append("".join(buffer))
                    buffer.clear()
                    had_splitter = True
                    return  # do not descend into splitter tag
                for child in node.children:
                    walk(child)

        walk(element)
        parts.append("".join(buffer))
        if had_splitter:
            return parts
        return None
