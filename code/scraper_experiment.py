import os
import uuid
from objects.builders.website_resolve import resolve_website
from pytesseract import pytesseract

from settings.system_defaults import TESSERACT_PATH, TEMP_FOLDER

pytesseract.tesseract_cmd = TESSERACT_PATH
os.makedirs(TEMP_FOLDER, exist_ok=True)

StartingURL = "https://gravitytales.com/story/i-bring-the-game-into-reality/chapter-200-11/"
process_id = str(uuid.uuid4())


def read_pages(start_page=StartingURL, parts_to_make=1):
    website = start_page.split("/")[2]
    try:
        parsing_process = resolve_website(website, process_id)
        parsing_process.parse_iterations(start_page, parts_to_make)

    except Exception as e:
        raise Exception(f"Processing failed: {str(e)}")


if __name__ == "__main__":
    start_part = StartingURL
    parts_num = int(input())
    read_pages(start_part, parts_num)
