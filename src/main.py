import logging

import cssutils

from settings.system_defaults import TESSERACT_PATH, OUTPUT_FILE_DIRECTORY, APPLICATION_LOGS_PATH
import os
from pytesseract import pytesseract
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from router import api_router
from background_tasks import lifespan

# Initialize system paths and folders
cssutils.log.setLevel(logging.CRITICAL)
pytesseract.tesseract_cmd = TESSERACT_PATH
os.makedirs(os.path.dirname(APPLICATION_LOGS_PATH), exist_ok=True)
os.makedirs(OUTPUT_FILE_DIRECTORY, exist_ok=True)

# Create FastAPI app
app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="frontend"), name="static")
app.include_router(api_router)
