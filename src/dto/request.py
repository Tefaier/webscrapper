from datetime import datetime
import json
from typing import Dict, Any

from objects.types.request_status import RequestStatus


class Request:
    def __init__(
        self,
        id,
        url,
        chapters,
        status,
        process_id,
        created_at,
        started_at,
        completed_at,
        details,
        expired,
    ):
        self.id: int = id
        self.url: str = url
        self.chapters: int = chapters
        self.status: RequestStatus = RequestStatus[status]
        self.process_id: str = process_id
        self.created_at: datetime = created_at
        self.started_at: datetime = started_at
        self.completed_at: datetime = completed_at
        self.details: Dict[str, Any] = json.loads(details) if details else {}
        self.expired: bool = expired
