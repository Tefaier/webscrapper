from typing import List, Optional

from bs4 import BeautifulSoup, PageElement

from objects.types.field_types import FieldTypes
from elements_finders import ElementsFinder
from elements_post_processings import ElementsPostProcessing


class ElementsCollector:
    def __init__(
        self,
        field_type: FieldTypes,
        finders: Optional[List[ElementsFinder]] = None,
        post_processings: Optional[List[ElementsPostProcessing]] = None,
    ) -> None:
        self.field_type: FieldTypes = field_type
        self.finders: List[ElementsFinder] = finders or []
        self.post_processings: List[ElementsPostProcessing] = post_processings or []

    def collect(self, soup: BeautifulSoup) -> List[PageElement]:
        search_from: Optional[List[PageElement]] = None

        # Apply searching steps consecutively
        for finder in self.finders:
            search_from = finder.find(soup, search_from)
        elements = search_from

        # Apply post-processing steps consecutively
        for processor in self.post_processings:
            elements = processor.process(soup, elements)

        return elements or []
