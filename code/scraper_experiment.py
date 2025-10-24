import uuid
from objects.parsing_handlers.parsing_process import ParsingProcess
from objects.builders.website_resolve import resolve_website
from settings_file import active_parser_dicts, active_process_dicts

StartingURL = "https://gravitytales.com/story/i-bring-the-game-into-reality/chapter-200-11/"
process_id = str(uuid.uuid4())


def write_log(part: int, paragraphs_clear: int, paragraphs_cleaned: int):
    print(f"Part {part} is done! {paragraphs_clear} were detected and {paragraphs_cleaned} were left")


def read_pages(start_page=StartingURL, parts_to_make=1):
    console_part = 1
    website = start_page.split("/")[2]
    try:
        parsing_process = resolve_website(website, process_id)

        result = parsing_process.parse_iterations(start_page, parts_to_make)
        result["process_id"] = process_id
        write_log(parts_to_make, result["processed"], result["processed"])

    except Exception as e:
        raise Exception(f"Processing failed: {str(e)}")


if __name__ == "__main__":
    start_part = StartingURL
    parts_num = int(input())
    read_pages(start_part, parts_num)
