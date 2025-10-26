import os

from objects.db.database_service import DatabaseService
from settings.system_defaults import DB_PATH

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

db = DatabaseService(DB_PATH)
