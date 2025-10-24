from typing import List, Optional

from bs4 import BeautifulSoup, PageElement

from objects.file_handlers.log_writer import LogWriter
from objects.types.field_types import FieldTypes
from objects.elements.elements_finders import ElementsFinder
from objects.elements.elements_post_processings import ElementsPostProcessing


class ElementsCollector:
    def __init__(
        self,
        log_writer: LogWriter,
        field_type: FieldTypes,
        finders: List[ElementsFinder],
        post_processings: List[ElementsPostProcessing],
    ) -> None:
        self.logger = log_writer.get_logger(type(self).__name__)
        self.field_type: FieldTypes = field_type
        self.finders: List[ElementsFinder] = finders
        self.post_processings: List[ElementsPostProcessing] = post_processings

    def collect(self, soup: BeautifulSoup) -> List[PageElement]:
        search_from: Optional[List[PageElement]] = None

        # Apply searching steps consecutively
        for finder in self.finders:
            search_from = finder.find(soup, search_from)
        elements = search_from

        # Apply post-processing steps consecutively
        before = len(elements)
        for processor in self.post_processings:
            elements = processor.process(soup, elements)
        self.logger.debug(f"Located {before} elements - {len(elements)} left after post processing")

        return elements or []
