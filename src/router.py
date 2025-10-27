from fastapi import APIRouter, Depends
import io
import os

from fastapi.responses import PlainTextResponse, StreamingResponse, HTMLResponse

from dto.models import ParseRequest, AddWebsiteRequest, DownloadResultRequest

from database import db
from objects.types.custom_exceptions import CommandException, DBOverlapException, InvalidUrlException
from settings.system_defaults import FINISHED_TASKS_LIFETIME, TEMP_FOLDER
import zipfile

api_router = APIRouter()


@api_router.get("/")
def index():
    return HTMLResponse(open("./frontend/index.html").read(), media_type="text/html", status_code=200)


@api_router.post("/requests")
def create_request(body: ParseRequest):
    url_value = body.url
    chapters_value = body.chapters
    try:
        if not url_value or not chapters_value:
            raise CommandException("URL and chapters are required")
        id = db.create_request(url_value, chapters_value)
        req_id = db.get_request(id)
        return PlainTextResponse(content=req_id, status_code=200)
    except (CommandException, InvalidUrlException) as e:
        return PlainTextResponse(content=e.message, status_code=400)
    except Exception as e:
        return PlainTextResponse(content=f"Unknown error: {e}", status_code=500)


@api_router.post("/add-website")
def add_website(body: AddWebsiteRequest):
    url_value = body.url
    if not url_value:
        return PlainTextResponse(content="URL is required", status_code=400)
    try:
        id = db.create_add_website(url_value)
        return PlainTextResponse(content="Successfully added your request", status_code=200)
    except (DBOverlapException, InvalidUrlException, CommandException) as e:
        return PlainTextResponse(content=e.message, status_code=400)
    except Exception as e:
        return PlainTextResponse(content=f"Unknown error: {e}", status_code=500)


@api_router.get("/download")
def download_result(query: DownloadResultRequest = Depends()):
    rid = query.req_id
    if not rid:
        return PlainTextResponse(content="Request id is not present", status_code=400)
    try:
        request = db.get_request_by_request_id(rid)
        if request is None:
            raise CommandException(f"Request with rid {rid} not found")
        if request.expired:
            raise CommandException(
                f"Request already expired, expiration time is {FINISHED_TASKS_LIFETIME} and task was finished at {request.completed_at}"
            )

        directory = os.path.join(TEMP_FOLDER, str(request.request_id))
        mem = io.BytesIO()
        with zipfile.ZipFile(mem, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, directory)
                    zf.write(file_path, arcname=arcname)
        mem.seek(0)
        return StreamingResponse(
            mem, media_type="application/zip", headers={"Content-Disposition": f'attachment; filename="Result.zip"'}
        )
    except CommandException as e:
        return PlainTextResponse(content=e.message, status_code=400)
    except Exception as e:
        return PlainTextResponse(content=f"Unknown error: {e}", status_code=500)
