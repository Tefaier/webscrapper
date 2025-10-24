from datetime import datetime
from typing import Optional, Dict, Any

from objects.db.database import RequestDatabase


class DatabaseService:
    def __init__(self, db_path: str = "requests.db"):
        self.db = RequestDatabase(db_path)

    async def create_request(self, url: str, chapters: int) -> int:
        """Create a new request and return its ID"""
        return self.db.create_request(url, chapters)

    async def start_processing(self, request_id: int, process_id: str):
        """Mark a request as in progress"""
        self.db.start_processing(request_id, process_id)

    async def complete_processing(self, request_id: int, details: Dict[str, Any], result_file: str, log_file: str):
        """Mark a request as completed with results"""
        self.db.complete_processing(request_id, details, result_file, log_file)

    async def fail_processing(self, request_id: int, details: Dict[str, Any], result_file: str, log_file: str):
        """Mark a request as failed with error message"""
        self.db.fail_processing(request_id, details, result_file, log_file)

