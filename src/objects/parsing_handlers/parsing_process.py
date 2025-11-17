from __future__ import annotations

from typing import Dict, Any

from objects.file_handlers.log_writer import LogWriter
from objects.parsing_handlers.content_parser import ContentParser
from objects.types.custom_exceptions import TargetNotFoundException
from objects.web_handlers.link_handler import LinkHandler


class ParsingProcess:
    """
    Coordinates content parsing and navigation across multiple iterations.

    Constructor expects ready-to-use ContentParser and LinkHandler instances.
    - ContentParser is responsible for opening the current URL and writing parsed output via its ElementsOrchestra.
    - LinkHandler is responsible for locating and following the next link based on the parsed DOM.

    The process ensures the underlying OutputWriter is closed on completion or on any error, and returns
    a structured result with progress and error information (if any).
    """

    def __init__(self, log_writer: LogWriter, parser: ContentParser, link_handler: LinkHandler) -> None:
        self.log_writer = log_writer
        self.logger = log_writer.get_logger(type(self).__name__)
        self.parser = parser
        self.link_handler = link_handler

    def parse_iterations(self, start_url: str, iterations: int) -> Dict[str, Any]:
        """
        Parse content starting from start_url for a given number of iterations.

        Returns a dictionary with fields:
            - success: bool
            - processed: int (number of successfully processed iterations)
            - start_url: str
            - last_url: str (the last URL that was processed or resolved)
            - finished_early: bool (optional, set if next link was not found before completing iterations)
            - error_type: str (optional)
            - error_message: str (optional)
        """
        current_url: str = start_url
        processed: int = 0
        result: Dict[str, Any] = {
            "success": False,
            "processed": 0,
            "start_url": start_url,
            "last_url": start_url,
        }
        try:
            # Iterate requested number of times
            for i in range(max(0, iterations)):
                # Parse current URL and write content
                self.parser.parse_content(current_url)

                # no need for resolving link at last chapter
                if i == iterations - 1:
                    processed += 1
                    break

                # Build soup for link detection after content is parsed
                soup = self.parser.get_soup(current_url)

                # Try to follow the next link; if missing, we finish early successfully
                try:
                    next_url = self.link_handler.navigate(current_url, soup)
                except TargetNotFoundException as e:
                    self.logger.warning(f"Didn't find link - early termination", exc_info=e)
                    processed += 1
                    result.update(
                        {
                            "success": True,
                            "processed": processed,
                            "last_url": current_url,
                            "finished_early": True,
                        }
                    )
                    return result

                # Step completed
                processed += 1
                current_url = next_url or current_url

            # All iterations completed
            result.update(
                {
                    "success": True,
                    "processed": processed,
                    "last_url": current_url,
                }
            )
            self.logger.debug("All processed - finishing")
            return result
        except Exception as e:
            self.logger.error(f"Failed at iteration {processed}", exc_info=e)
            result.update(
                {
                    "success": False,
                    "processed": processed,
                    "last_url": current_url,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                }
            )
            return result
        finally:
            self.parser.close()
            del self.log_writer
