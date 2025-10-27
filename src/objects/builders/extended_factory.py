import os
from typing import Type, Dict, Any, Optional, List
from typing_extensions import Self

from objects.builders.builder import BaseBuilder
from objects.file_handlers.log_writer import LogWriter
from objects.file_handlers.output_writers import TxtWriter, HtmlWriter, DocxWriter
from objects.parsing_handlers.content_parser import ContentParser
from objects.parsing_handlers.parsing_process import ParsingProcess
from objects.types.custom_exceptions import UnsupportedArgumentsException
from objects.web_handlers.driver_handler import DriverHandler
from objects.web_handlers.link_handler import LinkHandler
from objects.web_handlers.scroll_strategy import ScrollStrategy, NoScroll
from objects.web_handlers.block_screen_handler import (
    BlockScreenHandler,
    NoHandling,
    CollectedHandler,
    FieldInputHandler,
    ButtonClickHandler,
)
from objects.web_handlers.reload_handler import ReloadHandler
from objects.elements.elements_finders import ElementsFinder
from objects.elements.elements_collector import ElementsCollector
from objects.elements.elements_post_processings import (
    ElementsPostProcessing,
    VisibilityFilter,
    SubtreeRemovalFilter,
    TextNormalizer,
    RepeatsFilter,
)
from objects.elements.elements_orderer import ElementsOrderer
from objects.elements.elements_orchestra import ElementsOrchestra
from objects.types.field_types import FieldTypes
from objects.types.order_stategy import OrderStrategy
from settings.builders_defaults import *
from settings.system_defaults import OUTPUT_FILE_DIRECTORY


class ExtendedFactory:
    """
    Fluent factory to configure and wire parsing pipeline.

    Key features added:
    - Unique name assignment when registering repeated classes (finder/processor/collector/etc.)
    - Convenience helpers to create finders, post processors, collectors, orderer, orchestra
    - Web-handlers helpers (scroll, block-handlers, reload) and driver wiring
    - Parser and LinkHandler wiring helpers
    - Output writer configuration
    """

    def __init__(self, request_id: str):
        self.builder = BaseBuilder()
        self.rid = request_id
        # internal state for dynamic wiring and unique names
        self._counters: Dict[str, int] = {}
        self._driver_handler_name: Optional[str] = None
        self._orchestra_called: bool = False
        self._link_handler_called: bool = False
        self._link_collector_called: bool = False
        self._reload_handler_called: bool = False
        self._parser_called: bool = False
        self._create_defaults()

    # -------- defaults --------
    def _create_defaults(self):
        os.makedirs(f"{OUTPUT_FILE_DIRECTORY}/{self.rid}", exist_ok=True)
        self.builder.register(LOG_WRITER_NAME, LogWriter)
        self.builder.add_config(LOG_WRITER_NAME, {"full_path": f"{OUTPUT_FILE_DIRECTORY}/{self.rid}/log.txt"})

        # core endpoints
        self.builder.register(ORDERER_NAME, ElementsOrderer)
        self.builder.register(ORCHESTRA_NAME, ElementsOrchestra)
        self.builder.register(LINK_HANDLER_NAME, LinkHandler)
        self.builder.register(RELOAD_HANDLER_NAME, ReloadHandler)
        self.builder.register(PARSER_NAME, ContentParser)
        self.builder.register(PARSING_PROCESS_NAME, ParsingProcess)
        self.builder.add_config(
            PARSING_PROCESS_NAME,
            {"log_writer": f"${LOG_WRITER_NAME}", "parser": f"${PARSER_NAME}", "link_handler": f"${LINK_HANDLER_NAME}"},
        )

        # default strategies
        self.orderer(OrderStrategy.CONCAT)
        self.scroll(NoScroll)
        self.main_block_handler(NoHandling)
        self.output("txt")
        self.default_post_processing()

    # -------- basic API passthroughs --------
    def register(self, name: str, cls: Type) -> Self:
        self.builder.register(name, cls)
        return self

    def configure(self, config: Dict[str, Any]) -> Self:
        self.builder.configure(config)
        return self

    # -------- driver / selenium --------
    def selenium(self, is_undetected: bool, window_w: Optional[int] = None, window_h: Optional[int] = None) -> Self:
        self._driver_handler_name = f"${DRIVER_HANDLER_NAME}"
        self.builder.register(DRIVER_HANDLER_NAME, DriverHandler)
        self.builder.add_config(
            DRIVER_HANDLER_NAME,
            _clear_nones(
                {
                    "undetected_method": is_undetected,
                    "window_width": window_w,
                    "window_height": window_h,
                }
            ),
        )
        return self

    # -------- output --------
    def output(self, file_type: str, image_width: Optional[float] = None) -> Self:
        if file_type == "txt":
            self.builder.register(OUTPUT_WRITER_NAME, TxtWriter)
            self.builder.add_config(OUTPUT_WRITER_NAME, {"full_path": f"{OUTPUT_FILE_DIRECTORY}/{self.rid}/result.txt"})
        elif file_type == "html":
            self.builder.register(OUTPUT_WRITER_NAME, HtmlWriter)
            self.builder.add_config(OUTPUT_WRITER_NAME, {"full_path": f"{OUTPUT_FILE_DIRECTORY}/{self.rid}/result.html"})
        elif file_type == "docx":
            self.builder.register(OUTPUT_WRITER_NAME, DocxWriter)
            self.builder.add_config(
                OUTPUT_WRITER_NAME,
                _clear_nones({"full_path": f"{OUTPUT_FILE_DIRECTORY}/{self.rid}/result.docx", "image_width": image_width}),
            )
        else:
            raise UnsupportedArgumentsException(f"Unsupported file type: {file_type}")
        return self

    # -------- elements configuration helpers --------
    def finder(self, name: str, cls: Type[ElementsFinder], **cfg) -> Self:
        self.builder.register(name, cls)
        self.builder.add_config(name, {"log_writer": f"${LOG_WRITER_NAME}", **cfg})
        return self

    def post_processing(self, name: str, cls: Type[ElementsPostProcessing], **cfg) -> Self:
        self.builder.register(name, cls)
        self.builder.add_config(name, {"log_writer": f"${LOG_WRITER_NAME}", **cfg})
        return self

    def collector(
        self, name: str, field_type: FieldTypes, finders: List[str], post_processings: Optional[List[str]] = None
    ) -> Self:
        self.builder.register(name, ElementsCollector)
        self.builder.add_config(
            name,
            {
                "log_writer": f"${LOG_WRITER_NAME}",
                "field_type": field_type,
                "finders": [f"${f}" for f in (finders or [])],
                "post_processings": [f"${p}" for p in (post_processings or [])],
            },
        )
        return self

    def link_collector(self, finders: List[str], post_processings: Optional[List[str]] = None) -> Self:
        self._link_collector_called = True
        return self.collector(LINK_COLLECTOR_NAME, FieldTypes.Link, finders, post_processings)

    def orderer(self, strategy: OrderStrategy = OrderStrategy.CONCAT) -> Self:
        self.builder.add_config(ORDERER_NAME, {"log_writer": f"${LOG_WRITER_NAME}", "strategy": strategy})
        return self

    def orchestra(self, collectors: List[str], min_expected: Optional[int] = None, min_expected_text: Optional[int] = None) -> Self:
        self._orchestra_called = True
        self.builder.add_config(
            ORCHESTRA_NAME,
            _clear_nones(
                {
                    "log_writer": f"${LOG_WRITER_NAME}",
                    "collectors": [f"${c}" for c in collectors],
                    "orderer": f"${ORDERER_NAME}",
                    "output": f"${OUTPUT_WRITER_NAME}",
                    "min_expected": min_expected,
                    "min_expected_text": min_expected_text,
                }
            ),
        )
        return self

    # -------- web-handlers --------
    def scroll(self, cls: Type[ScrollStrategy], **cfg) -> Self:
        self.builder.register(SCROLL_NAME, cls)
        self.builder.add_config(SCROLL_NAME, {"log_writer": f"${LOG_WRITER_NAME}", **cfg})
        return self

    def block_handler(self, name: str, cls: Type[BlockScreenHandler], **cfg) -> Self:
        self.builder.register(name, cls)
        self.builder.add_config(name, {"log_writer": f"${LOG_WRITER_NAME}", **cfg})
        return self

    def main_block_handler(self, cls: Type[BlockScreenHandler], **cfg) -> Self:
        self.builder.register(MAIN_BLOCK_HANDLER_NAME, cls)
        self.builder.add_config(MAIN_BLOCK_HANDLER_NAME, {"log_writer": f"${LOG_WRITER_NAME}", **cfg})
        return self

    def reload_handler(self, **cfg) -> Self:
        self._reload_handler_called = True
        self.builder.add_config(
            RELOAD_HANDLER_NAME,
            _clear_nones({"log_writer": f"${LOG_WRITER_NAME}", "driver_handler": self._driver_handler_name, **cfg}),
        )
        return self

    def link_handler(
        self,
        press_link: Optional[bool] = None,
        reload_after: Optional[bool] = None,
        link_pure_click: Optional[bool] = None,
        wait_for_url_change_seconds: Optional[float] = None,
    ) -> Self:
        self._link_handler_called = True
        # override default link handler wiring
        self.builder.add_config(
            LINK_HANDLER_NAME,
            _clear_nones(
                {
                    "log_writer": f"${LOG_WRITER_NAME}",
                    "link_collector": f"${LINK_COLLECTOR_NAME}",
                    "driver_handler": self._driver_handler_name,
                    "press_link": press_link,
                    "reload_after": reload_after,
                    "link_pure_click": link_pure_click,
                    "wait_for_url_change_seconds": wait_for_url_change_seconds,
                }
            ),
        )
        return self

    def default_post_processing(self) -> Self:
        self.builder.register(f"{POST_PROCESSING_NAME}_default_vis", VisibilityFilter)
        self.builder.add_config(f"{POST_PROCESSING_NAME}_default_vis", {"log_writer": f"${LOG_WRITER_NAME}"})
        self.builder.register(f"{POST_PROCESSING_NAME}_default_sub", SubtreeRemovalFilter)
        self.builder.add_config(f"{POST_PROCESSING_NAME}_default_sub", {"log_writer": f"${LOG_WRITER_NAME}"})
        self.builder.register(f"{POST_PROCESSING_NAME}_default_nor", TextNormalizer)
        self.builder.add_config(f"{POST_PROCESSING_NAME}_default_nor", {"log_writer": f"${LOG_WRITER_NAME}"})
        self.builder.register(f"{POST_PROCESSING_NAME}_default_rep", RepeatsFilter)
        self.builder.add_config(f"{POST_PROCESSING_NAME}_default_rep", {"log_writer": f"${LOG_WRITER_NAME}"})
        return self

    # -------- parser wiring --------
    def _parser(self) -> Self:
        self._parser_called = True
        cfg = {
            "log_writer": f"${LOG_WRITER_NAME}",
            "orchestra": f"${ORCHESTRA_NAME}",
            "scroll_strategy": f"${SCROLL_NAME}",
            "block_handler": f"${MAIN_BLOCK_HANDLER_NAME}",
            "reload_handler": f"${RELOAD_HANDLER_NAME}",
            "driver_handler": self._driver_handler_name,
        }
        self.builder.add_config(PARSER_NAME, _clear_nones(cfg))
        return self

    # -------- finalize --------
    def finish(self) -> ParsingProcess:
        # ensure necessary things are created
        if not self._link_collector_called:
            raise UnsupportedArgumentsException(
                "Link collector is not configured. Call link_collector(...) before finish()."
            )
        if not self._orchestra_called:
            raise UnsupportedArgumentsException("Orchestra is not configured. Call orchestra(...) before finish().")
        # here to link driver in case it was created
        if not self._link_handler_called:
            self.link_handler()
        if not self._reload_handler_called:
            self.reload_handler()
        if not self._parser_called:
            self._parser()
        return self.builder.create(PARSING_PROCESS_NAME)


def _clear_nones(original: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in original.items() if v is not None}
