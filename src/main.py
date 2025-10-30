import logging

import cssutils

from settings.system_defaults import TEMP_FOLDER, TESSERACT_PATH
import os
from pytesseract import pytesseract
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from router import api_router
from background_tasks import lifespan

# Initialize system paths and folders
cssutils.log.setLevel(logging.CRITICAL)
pytesseract.tesseract_cmd = TESSERACT_PATH
os.makedirs(TEMP_FOLDER, exist_ok=True)

# Create FastAPI app
app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="frontend"), name="static")
app.include_router(api_router)
