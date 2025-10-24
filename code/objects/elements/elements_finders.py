from typing import List, Dict

from bs4 import BeautifulSoup, Tag, PageElement

from objects.file_handlers.log_writer import LogWriter


class ElementsFinder:
    def __init__(self, log_writer: LogWriter):
        self.logger = log_writer.get_logger(type(self).__name__)

    def find(self, soup: BeautifulSoup, search_from: List[PageElement] = None) -> List[PageElement]:
        ...


class ByAttributesFinder(ElementsFinder):
    def __init__(
        self,
        log_writer: LogWriter,
        search_types: List[str],
        search_limits: Dict[str, str] = None,
    ):
        super().__init__(log_writer)
        self.search_types = search_types
        self.search_limits = search_limits or {}

    def find(self, soup: BeautifulSoup, search_from: List[PageElement] = None) -> List[PageElement]:
        results: List[PageElement] = []
        if search_from is None or len(search_from) == 0:
            search_from = [soup]
        for origin in search_from:
            if isinstance(origin, Tag):
                results += origin.find_all(self.search_types, attrs=self.search_limits)
            elif isinstance(origin, PageElement):
                results.append(origin)
        self.logger.debug(f"Found {len(results)} elements (started from {len(search_from)})")
        return results


class ByTextFinder(ElementsFinder):
    def __init__(
        self,
        log_writer: LogWriter,
        search_types: List[str],
        inner_context: str,
    ):
        super().__init__(log_writer)
        self.search_types = search_types
        self.inner_context = inner_context

    def find(self, soup: BeautifulSoup, search_from: List[PageElement] = None) -> List[PageElement]:
        results: List[PageElement] = []
        if search_from is None or len(search_from) == 0:
            search_from = [soup]
        for origin in search_from:
            if isinstance(origin, Tag):
                results += origin.find_all(self.search_types, string=self.inner_context)
            elif isinstance(origin, PageElement):
                results.append(origin)
        self.logger.debug(f"Found {len(results)} elements (started from {len(search_from)})")
        return results


class ByCssSelectorFinder(ElementsFinder):
    def __init__(
        self,
        log_writer: LogWriter,
        selector: str,
    ):
        super().__init__(log_writer)
        self.selector = selector

    def find(self, soup: BeautifulSoup, search_from: List[PageElement] = None) -> List[PageElement]:
        results: List[PageElement] = []
        if search_from is None or len(search_from) == 0:
            search_from = [soup]
        for origin in search_from:
            if isinstance(origin, Tag):
                results += origin.select(self.selector)
            elif isinstance(origin, PageElement):
                results.append(origin)
        self.logger.debug(f"Found {len(results)} elements (started from {len(search_from)})")
        return results
