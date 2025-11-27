import logging

import cssutils

from settings.system_defaults import (
    TESSERACT_PATH,
    OUTPUT_FILE_DIRECTORY,
    APPLICATION_LOGS_PATH,
    CHROME_DIRECTORY,
    CHROME_UNDETECTED_DIRECTORY,
)
import os
from pytesseract import pytesseract
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from router import api_router
from background_tasks import lifespan

# Initialize system paths and folders
cssutils.log.setLevel(logging.CRITICAL)
if TESSERACT_PATH != "" and TESSERACT_PATH is not None:
    pytesseract.tesseract_cmd = TESSERACT_PATH
os.makedirs(os.path.dirname(APPLICATION_LOGS_PATH), exist_ok=True)
os.makedirs(OUTPUT_FILE_DIRECTORY, exist_ok=True)

if CHROME_DIRECTORY == CHROME_UNDETECTED_DIRECTORY:
    print(
        "Detected that your directory for usual chrome and undetected are the same - it is not recommended because usual chrome will pollute undetected cookies and history"
    )

# Create FastAPI app
app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="frontend"), name="static")
app.include_router(api_router)
