from __future__ import annotations

from typing import List, Tuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, PageElement
from bs4.element import Tag
import validators

from objects.elements.elements_collector import ElementsCollector
from objects.elements.elements_orderer import ElementsOrderer
from objects.file_handlers.log_writer import LogWriter
from objects.file_handlers.output_writers import OutputWriter
from objects.types.custom_exceptions import TargetNotFoundException
from objects.types.field_types import FieldTypes
from settings.elements_defaults import (
    LINK_INFO_PART,
    MIN_EXPECTED_PARAGRAPHS,
    MIN_EXPECTED_CHARS,
    IMAGE_GET_TIMEOUT_SECONDS,
)


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
        log_writer: LogWriter,
        collectors: List[ElementsCollector],
        orderer: ElementsOrderer,
        output: OutputWriter,
        min_expected: int = MIN_EXPECTED_PARAGRAPHS,
        min_expected_text: int = MIN_EXPECTED_CHARS,
    ) -> None:
        self.logger = log_writer.get_logger(type(self).__name__)
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
            message = f"Not enough elements collected. Expected at least {self.min_expected}, got {len(ordered)}"
            self.logger.error(message)
            raise TargetNotFoundException(message)
        char_count = sum([len(part[1].text) for part in ordered if part[0] == FieldTypes.Text])
        if char_count < self.min_expected_text:
            message = f"Not enough chars collected. Expected at least {self.min_expected_text}, got {char_count}"
            self.logger.error(message)
            raise TargetNotFoundException(message)

        for element in ordered:
            self._make_output(url, element)

    def _make_output(self, url: str, data: Tuple[FieldTypes, PageElement]):
        element_type, element = data
        if element_type == FieldTypes.Text:
            self.output.write_text(element.text)
        elif element_type == FieldTypes.Image and isinstance(element, Tag):
            try:
                for param in LINK_INFO_PART:
                    info = element.get(param)
                    if info is None:
                        continue
                    get_by = None
                    if validators.url(info):
                        get_by = info
                    else:
                        info = urljoin(url, info)
                        if validators.url(info):
                            get_by = info
                    if get_by is None:
                        continue
                    self.logger.debug(f"Started getting image with url: {get_by}")
                    response = requests.get(get_by, {"Referer": url}, timeout=IMAGE_GET_TIMEOUT_SECONDS)
                    content_type: str = response.headers.get("content-type")
                    if "image" not in content_type:
                        self.logger.warning(f"Received response with type {content_type} - image is ignored")
                        return
                    self.output.write_image(response.content, content_type[6:])
                    return
                self.logger.warning(f"Failed to get information about image url: {element.__repr__()}")
            except Exception as e:
                self.logger.warning("Encountered error in getting image", exc_info=e)
