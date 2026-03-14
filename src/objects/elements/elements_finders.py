from typing import List, Dict

from bs4 import BeautifulSoup, Tag, PageElement

from objects.file_handlers.log_writer import LogWriter
from settings.elements_defaults import DEFAULT_CACHE_SIZE
from collections import deque


class ElementsFinder:
    def __init__(self, log_writer: LogWriter, cache_size: int):
        self.logger = log_writer.get_logger(type(self).__name__)
        self._cache_size = max(1, int(cache_size))
        self._cache: Dict = {}  # key -> results (tuple of elements)
        self._cache_order: deque = deque([], cache_size + 1)  # most-recently used at the end

    def _make_cache_key(self, soup: BeautifulSoup, search_from: List[PageElement] = None):
        origins = [soup] if search_from is None or len(search_from) == 0 else search_from
        return (id(soup), tuple(id(o) for o in origins))

    def _touch_key(self, key):
        try:
            self._cache_order.remove(key)
        except ValueError:
            pass
        self._cache_order.append(key)
        while len(self._cache_order) > self._cache_size:
            lru_key = self._cache_order.popleft()
            self._cache.pop(lru_key, None)

    def _get_cached_results(self, soup: BeautifulSoup, search_from: List[PageElement] = None):
        key = self._make_cache_key(soup, search_from)
        cached = self._cache.get(key)
        if cached is not None:
            self._touch_key(key)
            return cached
        return None

    def _set_cached_results(self, soup: BeautifulSoup, search_from: List[PageElement], results: List[PageElement]):
        key = self._make_cache_key(soup, search_from)
        self._cache[key] = results
        self._touch_key(key)

    def find(self, soup: BeautifulSoup, search_from: List[PageElement] = None) -> List[PageElement]: ...


class ByAttributesFinder(ElementsFinder):
    def __init__(
        self,
        log_writer: LogWriter,
        search_types: List[str],
        search_limits: Dict[str, str] = None,
        cache_size: int = DEFAULT_CACHE_SIZE,
    ):
        super().__init__(log_writer, cache_size)
        self.search_types = search_types
        self.search_limits = search_limits or {}

    def find(self, soup: BeautifulSoup, search_from: List[PageElement] = None) -> List[PageElement]:
        cached = self._get_cached_results(soup, search_from)
        if cached is not None:
            self.logger.debug(f"Found {len(cached)} elements (from cache)")
            return cached

        results: List[PageElement] = []
        origins = [soup] if search_from is None else search_from
        for origin in origins:
            if isinstance(origin, Tag):
                results += origin.find_all(self.search_types, attrs=self.search_limits)
            elif isinstance(origin, PageElement):
                results.append(origin)

        self._set_cached_results(soup, search_from, results)
        self.logger.debug(f"Found {len(results)} elements (started from {len(origins)})")
        return results


class ByTextFinder(ElementsFinder):
    def __init__(
        self,
        log_writer: LogWriter,
        search_types: List[str],
        inner_context: str,
        cache_size: int = DEFAULT_CACHE_SIZE,
    ):
        super().__init__(log_writer, cache_size)
        self.search_types = search_types
        self.inner_context = inner_context

    def find(self, soup: BeautifulSoup, search_from: List[PageElement] = None) -> List[PageElement]:
        cached = self._get_cached_results(soup, search_from)
        if cached is not None:
            self.logger.debug(f"Found {len(cached)} elements (from cache)")
            return cached

        results: List[PageElement] = []
        origins = [soup] if search_from is None or len(search_from) == 0 else search_from
        for origin in origins:
            if isinstance(origin, Tag):
                results += origin.find_all(self.search_types, string=self.inner_context)
            elif isinstance(origin, PageElement):
                results.append(origin)
        self._set_cached_results(soup, search_from, results)
        self.logger.debug(f"Found {len(results)} elements (started from {len(origins)})")
        return results


class ByCssSelectorFinder(ElementsFinder):
    def __init__(
        self,
        log_writer: LogWriter,
        selector: str,
        cache_size: int = DEFAULT_CACHE_SIZE,
    ):
        super().__init__(log_writer, cache_size)
        self.selector = selector

    def find(self, soup: BeautifulSoup, search_from: List[PageElement] = None) -> List[PageElement]:
        cached = self._get_cached_results(soup, search_from)
        if cached is not None:
            self.logger.debug(f"Found {len(cached)} elements (from cache)")
            return cached

        results: List[PageElement] = []
        origins = [soup] if search_from is None or len(search_from) == 0 else search_from
        for origin in origins:
            if isinstance(origin, Tag):
                results += origin.select(self.selector)
            elif isinstance(origin, PageElement):
                results.append(origin)
        self._set_cached_results(soup, search_from, results)
        self.logger.debug(f"Found {len(results)} elements (started from {len(origins)})")
        return results
