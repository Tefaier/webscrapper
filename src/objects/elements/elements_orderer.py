from __future__ import annotations

from enum import Enum
from typing import List, Tuple, Iterable

from bs4 import Tag, PageElement

from objects.file_handlers.log_writer import LogWriter
from objects.types.field_types import FieldTypes
from objects.types.order_stategy import OrderStrategy


class ElementsOrderer:
    """
    Orders elements received as multiple (FieldTypes, List[PageElement]) pairs
    into a single list of (FieldTypes, PageElement) tuples using the configured strategy.

    Example usage:
        orderer = ElementsOrderer(OrderStrategy.BY_SOURCELINE)
        result = orderer.order(
            (FieldTypes.Text, text_elements),
            (FieldTypes.Image, image_elements),
        )
    """

    def __init__(self, log_writer: LogWriter, strategy: OrderStrategy = OrderStrategy.CONCAT):
        self.logger = log_writer.get_logger(type(self).__name__)
        self.strategy = strategy

    def order(self, typed_lists: List[Tuple[FieldTypes, List[PageElement]]]) -> List[Tuple[FieldTypes, PageElement]]:
        # Flatten into (field_type, element, seq_idx, elem_idx) to preserve stability
        flattened: List[Tuple[FieldTypes, PageElement, int, int]] = []
        for seq_idx, pair in enumerate(typed_lists):
            if not isinstance(pair, tuple) or len(pair) != 2:
                raise ValueError("Each argument must be a tuple: (FieldTypes, List[PageElement])")
            field_type, elements = pair
            if not isinstance(field_type, FieldTypes):
                raise ValueError("First item of each tuple must be a FieldTypes value")
            if not isinstance(elements, list):
                raise ValueError("Second item of each tuple must be a list of PageElement")

            for elem_idx, element in enumerate(elements):
                flattened.append((field_type, element, seq_idx, elem_idx))

        if self.strategy == OrderStrategy.CONCAT:
            return [(ft, e) for (ft, e, _si, _ei) in flattened]

        if self.strategy == OrderStrategy.BY_TYPE:
            return [(ft, e) for (ft, e, _si, _ei) in sorted(flattened, key=ElementsOrderer.field_type_sorting)]

        if self.strategy == OrderStrategy.BY_SOURCELINE:
            return [(ft, e) for (ft, e, _si, _ei) in sorted(flattened, key=ElementsOrderer.source_line_sorting)]

        message = f"Unknown strategy of concatenating was used {self.strategy}"
        self.logger.error(message)
        raise ValueError(message)

    @staticmethod
    def field_type_sorting(item: Tuple[FieldTypes, PageElement, int, int]):
        ft, el, si, ei = item
        return ft.value, si, ei

    @staticmethod
    def source_line_sorting(item: Tuple[FieldTypes, PageElement, int, int]):
        ft, el, si, ei = item
        if isinstance(el, Tag):
            # BeautifulSoup Tag may expose sourceline when using lxml parser
            sl = getattr(el, "sourceline", None)
            sp = getattr(el, "sourcepos", None)
            if sl is not None and sp is not None:
                # Items with sourceline come first, sorted by line number
                return 0, sl, sp, si, ei
        # Fallback: place after sourceline items, maintaining original stability
        return 1, 0, 0, si, ei
