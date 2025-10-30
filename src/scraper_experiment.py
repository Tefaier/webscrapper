import os
import uuid

from dto.request import Request
from objects.builders.website_resolve import resolve_website
from pytesseract import pytesseract

from settings.system_defaults import TESSERACT_PATH, TEMP_FOLDER

pytesseract.tesseract_cmd = TESSERACT_PATH
os.makedirs(TEMP_FOLDER, exist_ok=True)

StartingURL = ""
request_id = str(uuid.uuid4())


def read_pages(start_page=StartingURL, parts_to_make=1):
    website = start_page.split("/")[2]
    try:
        parsing_process = resolve_website(
            website, Request(0, start_page, parts_to_make, "ACTIVE", "TXT", request_id, None, None, None, None, False)
        )
        parsing_process.parse_iterations(start_page, parts_to_make)

    except Exception as e:
        raise Exception(f"Processing failed: {str(e)}")


if __name__ == "__main__":
    start_part = StartingURL
    parts_num = int(input())
    read_pages(start_part, parts_num)
