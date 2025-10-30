from typing import List

from bs4 import BeautifulSoup, NavigableString, Tag, PageElement
from selenium.webdriver.chrome.webdriver import WebDriver

from objects.elements.elements_finders import ElementsFinder
from objects.file_handlers.log_writer import LogWriter
from objects.types.custom_exceptions import UnsupportedArgumentsException
from settings.elements_defaults import FILTER_NO_MEANING, SPACES_NORMALIZATION, SYMBOLS_CONVERTION, REPEAT_TOLERANCE
from utils.text_functions import (
    string_with_meaning,
    string_with_style,
    convert_utf8_symbols,
    fix_bad_detections,
    check_is_same,
)
from utils.web_functions import (
    extract_all_styles,
    check_element_visibility,
    take_element_viewed_content,
    replace_element_with_text,
)


class ElementsPostProcessing:
    def __init__(self, log_writer: LogWriter):
        self.logger = log_writer.get_logger(type(self).__name__)

    def process(self, soup: BeautifulSoup, elements: List[PageElement]) -> List[PageElement]:
        ...


class SidesCutFiltering(ElementsPostProcessing):
    def __init__(self, log_writer: LogWriter, cut_from_beginning: int = 0, cut_from_ending: int = 0):
        super().__init__(log_writer)
        self.from_begin: int = max(0, cut_from_beginning)
        self.from_end: int = max(0, cut_from_ending)

    def process(self, soup: BeautifulSoup, elements: List[PageElement]) -> List[PageElement]:
        if len(elements) >= self.from_begin + self.from_end:
            return elements[self.from_begin : -self.from_end]
        self.logger.debug(f"Full cut was made due to only {len(elements)} being present")
        return []


class ExactElementTaker(ElementsPostProcessing):
    def __init__(self, log_writer: LogWriter, take_at_index: int = 0):
        super().__init__(log_writer)
        self.index: int = take_at_index

    def process(self, soup: BeautifulSoup, elements: List[PageElement]) -> List[PageElement]:
        if len(elements) > self.index:
            return [elements[self.index]]
        message = (
            f"Wanted to have at least {self.index + 1} elements for taking exact but actual count was {len(elements)}"
        )
        self.logger.error(message)
        raise UnsupportedArgumentsException(message)


class VisibilityFilter(ElementsPostProcessing):
    def __init__(self, log_writer: LogWriter):
        super().__init__(log_writer)
        self.css_classes_info = {}

    def process(self, soup: BeautifulSoup, elements: List[PageElement]) -> List[PageElement]:
        self.css_classes_info = extract_all_styles(soup)
        before = len(elements)
        elements = [element for element in elements if check_element_visibility(self.css_classes_info, element)]
        self.logger.debug(f"Filter result: {before}->{len(elements)}")
        for element in elements:
            self.recursively_check(element)
        return elements

    def recursively_check(self, element: PageElement):
        if isinstance(element, Tag):
            for child in element.contents:
                if not check_element_visibility(self.css_classes_info, child):
                    self.logger.debug("Sub element extracted")
                    child.extract()
                    continue
                self.recursively_check(child)


class JammedTextConverter(ElementsPostProcessing):
    def __init__(
        self,
        log_writer: LogWriter,
        jammed_finder: ElementsFinder = None,
        driver: WebDriver = None,
        expected_languages: List[str] = None,
        try_fix_text: bool = True,
    ):
        super().__init__(log_writer)
        self.driver = driver
        self.jammed_finder = jammed_finder
        self.expected_languages = expected_languages if expected_languages is not None else ["eng"]
        # self.jammed_classes = jammed_classes if jammed_classes is not None else ["jum", "jmbl"]
        self.fix = try_fix_text

    def process(self, soup: BeautifulSoup, elements: List[PageElement]) -> List[PageElement]:
        if self.driver is None:
            return elements
        return [
            replace_element_with_text(soup, element, self._convert_to_text(element))
            if self._check_element_is_jammed(soup, element)
            else element
            for element in elements
        ]

    def _convert_to_text(self, element: Tag) -> str:
        result = take_element_viewed_content(self.driver, self.expected_languages, element)
        self.logger.debug(f"Convertaion result: {result}")
        if self.fix:
            result = fix_bad_detections(result)
            self.logger.debug(f"Fixing result: {result}")
        return result

    def _check_element_is_jammed(self, soup: BeautifulSoup, element: PageElement) -> bool:
        if isinstance(element, Tag):
            result = element.find("img") is not None or len(self.jammed_finder.find(soup, [element])) > 0
        else:
            result = False
        if result:
            self.logger.debug(f"Element {element.__repr__()} was deemed jammed")
        return result


class SubtreeRemovalFilter(ElementsPostProcessing):
    def __init__(self, log_writer: LogWriter):
        super().__init__(log_writer)

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
        self.logger.debug(f"Filter result: {len(elements)}->{len(filtered)}")
        return filtered


class ExcludeByCollectorFilter(ElementsPostProcessing):
    """
    Uses a provided ElementsCollector to find elements in given and excludes them from the given list.
    Only elements present in both the input list and the collector's results are removed.
    """

    def __init__(self, log_writer: LogWriter, finder: ElementsFinder):
        super().__init__(log_writer)
        self.finder = finder

    def process(self, soup: BeautifulSoup, elements: List[PageElement]) -> List[PageElement]:
        to_exclude = self.finder.find(soup, elements)
        if not to_exclude:
            return elements
        exclude_ids = {id(e) for e in to_exclude}
        filtered = [e for e in elements if id(e) not in exclude_ids]
        self.logger.debug(f"Filter result: {len(elements)}->{len(filtered)}")
        return filtered


class SplitTagContentByInnerTags(ElementsPostProcessing):
    """
    For Tag elements, splits their textual content by occurrences of inner tags whose names are provided.
    Replaces such Tag elements with multiple NavigableStrings (including empty segments when separators are consecutive).
    Non-Tag elements are left untouched. If no splitter tag found inside a Tag, the element is kept as-is.
    """

    def __init__(self, log_writer: LogWriter, split_tag_names: List[str]):
        super().__init__(log_writer)
        self.split_names = {name.lower() for name in split_tag_names}

    def process(self, soup: BeautifulSoup, elements: List[PageElement]) -> List[PageElement]:
        before = len(elements)
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
        self.logger.debug(f"Split result: {before}->{len(result)}")
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


class TextNormalizer(ElementsPostProcessing):
    def __init__(
        self,
        log_writer: LogWriter,
        filter_no_meaning: bool = FILTER_NO_MEANING,
        spaces_normalization: bool = SPACES_NORMALIZATION,
        symbols_convertion: bool = SYMBOLS_CONVERTION,
    ):
        super().__init__(log_writer)
        self.filter_no_meaning = filter_no_meaning
        self.space_normalization = spaces_normalization
        self.symbols_convertion = symbols_convertion

    def process(self, soup: BeautifulSoup, elements: List[PageElement]) -> List[PageElement]:
        if self.filter_no_meaning:
            elements = list(filter(lambda el: self._check_meaning(el), elements))
        if self.space_normalization:
            elements = [
                replace_element_with_text(soup, element, string_with_style(element.text)) for element in elements
            ]
        if self.symbols_convertion:
            elements = [
                replace_element_with_text(soup, element, convert_utf8_symbols(element.text)) for element in elements
            ]

        return elements

    def _check_meaning(self, element: PageElement) -> bool:
        result = string_with_meaning(element.text)
        if not result:
            self.logger.debug(f"Deemed element to have no meaning: {element.__repr__()}")
        return result


class RepeatsFilter(ElementsPostProcessing):
    def __init__(self, log_writer: LogWriter, tolerance: int = REPEAT_TOLERANCE):
        super().__init__(log_writer)

        self.tolerance = max(0, tolerance)
        self.last_string = ""

    def process(self, soup: BeautifulSoup, elements: List[PageElement]) -> List[PageElement]:
        return [element for element in elements if self._check_condition(element)]

    def _check_condition(self, element: PageElement) -> bool:
        text = element.text
        is_same = check_is_same(self.last_string, text, self.tolerance)
        if not is_same:
            self.last_string = element.text
        else:
            self.logger.debug(f"Deemed element to be a repetition: {element.__repr__()} prev: {self.last_string}")
        return not is_same
