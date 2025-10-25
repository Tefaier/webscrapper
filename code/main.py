from objects.db.request_database import RequestDatabase
from settings.system_defaults import DB_PATH, TEMP_FOLDER, TESSERACT_PATH
import os
from pytesseract import pytesseract

pytesseract.tesseract_cmd = TESSERACT_PATH
os.makedirs(TEMP_FOLDER, exist_ok=True)
db = RequestDatabase(DB_PATH)
