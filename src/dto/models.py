from uuid import UUID
from pydantic import BaseModel

class ParseRequest(BaseModel):
    url: str
    chapters: int
    file_extension: str

class AddWebsiteRequest(BaseModel):
    url: str

class DownloadResultRequest(BaseModel):
    req_id: UUID
