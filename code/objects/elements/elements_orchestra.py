from __future__ import annotations

from typing import List, Tuple

import requests
from bs4 import BeautifulSoup, PageElement
from bs4.element import Tag
import validators

from objects.elements.elements_collector import ElementsCollector
from objects.elements.elements_orderer import ElementsOrderer
from objects.output_writers import OutputWriter
from objects.types.custom_exceptions import TargetNotFoundException
from objects.types.field_types import FieldTypes
from settings import link_info_part


class ElementsOrchestra:
    """
    Coordinates collection, ordering, validation and output of scraped elements.

    - collectors: list of ElementsCollector that fetch elements per FieldType
    - orderer: ElementsOrderer that merges and orders results across collectors
    - output: OutputWriter that receives the final ordered elements
    - min_expected: minimal number of elements expected; if not met, raises TargetNotFoundException
    - min_expected_text: minimal number of characters expected; if not met, raises TargetNotFoundException
    """

    def __init__(
        self,
        collectors: List[ElementsCollector],
        orderer: ElementsOrderer,
        output: OutputWriter,
        min_expected: int = 1,
        min_expected_text: int = 1,
    ) -> None:
        self.collectors = collectors
        self.orderer = orderer
        self.output = output
        self.min_expected = max(0, min_expected)
        self.min_expected_text = max(0, min_expected_text)

    def run(self, url: str, soup: BeautifulSoup):
        # Collect per collector
        typed_lists = [(collector.field_type, collector.collect(soup)) for collector in self.collectors]

        # Order using configured strategy
        ordered: List[Tuple[FieldTypes, PageElement]] = self.orderer.order(typed_lists)

        # Validation
        if len(ordered) < self.min_expected:
            raise TargetNotFoundException(
                f"Not enough elements collected. Expected at least {self.min_expected}, got {len(ordered)}"
            )
        char_count = sum([len(part[1].text) for part in ordered if part[0] == FieldTypes.Text])
        if char_count < self.min_expected_text:
            raise TargetNotFoundException(
                f"Not enough chars collected. Expected at least {self.min_expected_text}, got {char_count}"
            )

        for element in ordered:
            self._make_output(url, element)

    def _make_output(self, url: str, data: Tuple[FieldTypes, PageElement]):
        element_type, element = data
        if element_type == FieldTypes.Text:
            self.output.write_text(element.text)
        elif element_type == FieldTypes.Image and isinstance(element, Tag):
            try:
                for param in link_info_part:
                    info = element.get(param)
                    if info is None:
                        continue
                    if validators.url(info):
                        self.output.write_image(requests.get(info).content)
                        return
                    info = "/".join(url.split('/')[:3]) + info
                    if validators.url(info):
                        self.output.write_image(requests.get(info).content)
                        return
            except Exception as e:
                print(f"Encountered error in getting image: {e}")
