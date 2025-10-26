from typing import Optional, Dict, Any, List
from uuid import UUID

import validators

from objects.types.custom_exceptions import DBOverlapException, InvalidUrlException, CommandException
from utils.web_functions import get_domain
from dto.add_website import AddWebsite
from dto.request import Request
from objects.db.add_website_database import AddWebsiteDatabase
from objects.db.request_database import RequestDatabase
from settings.system_defaults import FINISHED_TASKS_LIFETIME, MAX_CHAPTERS_COUNT, MAX_NEW_WEBSITE_REQUESTS
from objects.builders.website_resolve import recognized_websites


class DatabaseService:
    def __init__(self, db_path: str = "app.db"):
        self.request_dao = RequestDatabase(db_path)
        self.add_dao = AddWebsiteDatabase(db_path)

    def get_all_add_websites(self) -> List[AddWebsite]:
        """Get all add website request"""
        return self.add_dao.get_all()

    def create_add_website(self, url: str) -> int:
        """Get all add website request"""
        domain = get_domain(url)
        if domain is None:
            raise InvalidUrlException(f"{url} is invalid url")
        if self.add_dao.get_count() > MAX_NEW_WEBSITE_REQUESTS:
            raise CommandException(f"Maximum number of requests for new website reached - try again later")
        id = self.add_dao.insert(domain)
        if id is None:
            raise DBOverlapException(f"{domain} is already present")
        return id

    def get_add_websites_count(self) -> int:
        """Get all add website request"""
        return self.add_dao.get_count()

    def get_add_website_by_url(self, url: str) -> Optional[AddWebsite]:
        """Get all add website request"""
        return self.add_dao.get_by_url(url)

    def get_request(self, id: int) -> Optional[Request]:
        """Get request by id or None"""
        return self.request_dao.get_request(id)
    
    def get_request_by_process_id(self, rid: UUID) -> Optional[Request]:
        """Get request by process_id or None"""
        return self.request_dao.get_request_by_request_id(rid)

    def create_request(self, url: str, chapters: int) -> int:
        """Create a new request and return its ID"""
        if not validators.url(url): # type: ignore
            raise InvalidUrlException(f"URL is invalid {url}")
        if get_domain(url) not in recognized_websites:
            raise CommandException(f"Unknown domain - {get_domain(url)}")
        if chapters <= 0:
            raise CommandException("Chapters must be greater than 0")
        if chapters > MAX_CHAPTERS_COUNT:
            raise CommandException(f"You can at most request {MAX_CHAPTERS_COUNT} chapters but {chapters} were requested")
        return self.request_dao.create_request(url, chapters)

    def start_processing(self, request_id: int, process_id: str):
        """Mark a request as in progress"""
        self.request_dao.start_processing(request_id, process_id)

    def complete_processing(self, request_id: int, details: Dict[str, Any], result_file: str, log_file: str):
        """Mark a request as completed with results"""
        self.request_dao.complete_processing(request_id, details, result_file, log_file)

    def fail_processing(self, request_id: int, details: Dict[str, Any], result_file: str, log_file: str):
        """Mark a request as failed with error message"""
        self.request_dao.fail_processing(request_id, details, result_file, log_file)

    def get_pending_requests(self, max_count: int) -> List[int]:
        """Get oldest CREATED requests and mark them as ACTIVE"""
        return self.request_dao.claim_pending_requests(max_count)

    def get_expired_requests(self) -> List[int]:
        """Get requests that are finished and old enough to be set as expired"""
        return self.request_dao.claim_expired_requests(FINISHED_TASKS_LIFETIME)
