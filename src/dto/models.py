from uuid import UUID
from pydantic import BaseModel, HttpUrl

class ParseRequest(BaseModel):
    url: str
    chapters: int

class AddWebsiteRequest(BaseModel):
    url: str

class DownloadResultRequest(BaseModel):
    req_id: UUID
