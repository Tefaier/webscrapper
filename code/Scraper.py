from Objects import Process, Parser
from Settings import active_parser_dicts, active_process_dicts

StartingURL = "https://fast.novelupdates.net/book/a-budding-scientist-in-a-fantasy-world/chapter-97"
def write_log(part: int, paragraphs_clear: int, paragraphs_cleaned: int):
    print(f"Part {part} is done! {paragraphs_clear} were detected and {paragraphs_cleaned} were left")

def read_pages(start_page = StartingURL, parts_to_make = 1):
    console_part = 1
    website = start_page.split("/")[2]
    try:
        active_process = Process(active_process_dicts[website])
        active_parser = Parser(active_process, active_parser_dicts[website])
    except:
        raise Exception("Unsupported error occurred during initialisation")
    active_parser.set_url(start_page, website)
    try:
        while console_part <= parts_to_make:
            active_parser.set_url(active_parser.process_page(), website)
            write_log(console_part, len(active_parser.text), len(active_parser.processed_text))
            console_part += 1
    finally:
        active_process.closing()
        del(active_process)
        del(active_parser)


if __name__ == "__main__":
    start_part = StartingURL
    parts_num = int(input())
    read_pages(start_part, parts_num)
