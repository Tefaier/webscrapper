from datetime import datetime
from typing import Optional, Dict, Any, List

from dto.add_website import AddWebsite
from dto.request import Request
from objects.db.add_website_database import AddWebsiteDatabase
from objects.db.request_database import RequestDatabase
from settings.system_defaults import FINISHED_TASKS_LIFETIME


class DatabaseService:
    def __init__(self, db_path: str = "app.db"):
        self.request_dao = RequestDatabase(db_path)
        self.add_dao = AddWebsiteDatabase(db_path)

    async def get_all_add_websites(self) -> List[AddWebsite]:
        """Get all add website request"""
        return self.add_dao.get_all()

    async def create_add_website(self, url: str) -> int:
        """Get all add website request"""
        return self.add_dao.insert(url)

    async def get_add_websites_count(self) -> int:
        """Get all add website request"""
        return self.add_dao.get_count()

    async def get_add_website_by_url(self, url: str) -> Optional[AddWebsite]:
        """Get all add website request"""
        return self.add_dao.get_by_url(url)

    async def get_request(self, id: int) -> Optional[Request]:
        """Get request by id or None"""
        return self.request_dao.get_request(id)

    async def create_request(self, url: str, chapters: int) -> int:
        """Create a new request and return its ID"""
        return self.request_dao.create_request(url, chapters)

    async def start_processing(self, request_id: int, process_id: str):
        """Mark a request as in progress"""
        self.request_dao.start_processing(request_id, process_id)

    async def complete_processing(self, request_id: int, details: Dict[str, Any], result_file: str, log_file: str):
        """Mark a request as completed with results"""
        self.request_dao.complete_processing(request_id, details, result_file, log_file)

    async def fail_processing(self, request_id: int, details: Dict[str, Any], result_file: str, log_file: str):
        """Mark a request as failed with error message"""
        self.request_dao.fail_processing(request_id, details, result_file, log_file)

    async def get_pending_requests(self, max_count: int) -> List[int]:
        """Get oldest CREATED requests and mark them as ACTIVE"""
        return self.request_dao.claim_pending_requests(max_count)

    async def get_expired_requests(self) -> List[int]:
        """Get requests that are finished and old enough to be set as expired"""
        return self.request_dao.claim_expired_requests(FINISHED_TASKS_LIFETIME)
