from uuid import UUID
from typing import Optional
from pydantic import BaseModel


class ParseRequest(BaseModel):
    url: str
    chapters: int
    file_extension: str
    lifetime_seconds: Optional[int] = None


class AddWebsiteRequest(BaseModel):
    url: str


class DownloadResultRequest(BaseModel):
    req_id: UUID
