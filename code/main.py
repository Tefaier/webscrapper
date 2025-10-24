import uuid

from objects.builders.website_resolve import resolve_website
from objects.db.database import RequestDatabase
from settings.system_defaults import DB_PATH, TEMP_FOLDER, TESSERACT_PATH
import os
from pytesseract import pytesseract

pytesseract.tesseract_cmd = TESSERACT_PATH
os.makedirs(TEMP_FOLDER, exist_ok=True)
db = RequestDatabase(DB_PATH)


def read_pages(process_id, start_page, parts_to_make=1):
    website = start_page.split("/")[2]
    try:
        parsing_process = resolve_website(website, process_id)
        parsing_process.parse_iterations(start_page, parts_to_make)

    except Exception as e:
        raise Exception(f"Processing failed: {str(e)}")


@app.post("/process")
async def process_request(request: Request):
    # Create initial db record
    request_id = await db.create_request(params)

    try:
        # Start processing
        process_id = generate_process_id()  # Your logic here
        await db.start_processing(request_id, process_id)

        # Your processing logic here
        result = await process_request(request.data)

        # Store results
        await db.complete_processing(request_id, result)

        return {"status": "completed", "result": result}

    except Exception as e:
        await db.fail_processing(request_id, str(e))
        raise e

