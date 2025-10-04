from typing import List, Dict

from bs4 import BeautifulSoup, Tag, PageElement


class ElementsFinder:
    def find(self, soup: BeautifulSoup, search_from: List[PageElement] = None) -> List[PageElement]: ...


class ByAttributesFinder(ElementsFinder):
    def __init__(
            self,
            search_types: str,
            search_limits: Dict[str, str] = None,
    ):
        self.search_types = search_types
        self.search_limits = search_limits if search_limits is not None else {}

    def find(self, soup: BeautifulSoup, search_from: List[PageElement] = None) -> List[PageElement]:
        results: List[PageElement] = []
        if search_from is None or len(search_from) == 0:
            search_from = soup
        for origin in search_from:
            if isinstance(origin, Tag):
                results += origin.find_all(self.search_types, self.search_limits)
            elif isinstance(origin, PageElement):
                results.append(origin)
        return results


class ByTextFinder(ElementsFinder):
    def __init__(
            self,
            search_types: str,
            inner_context: str,
    ):
        self.search_types = search_types
        self.inner_context = inner_context

    def find(self, soup: BeautifulSoup, search_from: List[PageElement] = None) -> List[PageElement]:
        results: List[PageElement] = []
        if search_from is None or len(search_from) == 0:
            search_from = soup
        for origin in search_from:
            if isinstance(origin, Tag):
                results += origin.find_all(self.search_types, string=self.inner_context)
            elif isinstance(origin, PageElement):
                results.append(origin)
        return results


class ByCssSelectorFinder(ElementsFinder):
    def __init__(
            self,
            selector: str,
    ):
        self.selector = selector

    def find(self, soup: BeautifulSoup, search_from: List[PageElement] = None) -> List[PageElement]:
        results: List[PageElement] = []
        if search_from is None or len(search_from) == 0:
            search_from = soup
        for origin in search_from:
            if isinstance(origin, Tag):
                results += origin.select(self.selector)
            elif isinstance(origin, PageElement):
                results.append(origin)
        return results
