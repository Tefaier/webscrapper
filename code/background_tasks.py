from objects.builders.website_resolve import resolve_website


def read_pages(process_id, start_page, parts_to_make=1):
    website = start_page.split("/")[2]
    try:
        parsing_process = resolve_website(website, process_id)
        parsing_process.parse_iterations(start_page, parts_to_make)

    except Exception as e:
        raise Exception(f"Processing failed: {str(e)}")
