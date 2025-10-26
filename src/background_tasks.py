from contextlib import asynccontextmanager
import asyncio
import os
import shutil
import logging
from fastapi import FastAPI
from objects.builders.website_resolve import resolve_website
from objects.db.database_service import DatabaseService
from settings.system_defaults import DB_PATH, TEMP_FOLDER
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

scheduler = AsyncIOScheduler()
db = DatabaseService(DB_PATH)
logger = logging.getLogger(__name__)
MAX_ACTIVE_PROCESSES = 5  # Maximum parallel processing tasks

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        scheduler.add_job(
            process_waiting_requests,
            trigger=IntervalTrigger(minutes=1),
            id="process_waiting_requests",
            replace_existing=True
        )
        scheduler.add_job(
            clear_expired_requests,
            trigger=IntervalTrigger(hours=1),
            id="clear_expired_requests",
            replace_existing=True
        )
        scheduler.start()
        yield
    finally:
        scheduler.shutdown()

async def process_waiting_requests():
    """Process pending requests with parallel execution"""
    try:
        # Claim pending requests up to max parallel processes
        request_ids = db.request_dao.claim_pending_requests(MAX_ACTIVE_PROCESSES)
        
        if not request_ids:
            return

        logger.info(f"Processing {len(request_ids)} pending requests")
        
        # Run processing in parallel
        await asyncio.gather(*[
            read_pages(request.process_id, request.url, request.chapters)
            for request in (db.request_dao.get_request(rid) for rid in request_ids)
            if request
        ])

    except Exception as e:
        logger.error(f"Error processing requests: {str(e)}")
        raise

async def clear_expired_requests():
    """Clean up expired requests and their storage folders"""
    try:
        # Claim expired requests (older than 24 hours)
        expired_ids = db.request_dao.claim_expired_requests(timedelta(hours=24))
        
        if not expired_ids:
            return

        logger.info(f"Cleaning up {len(expired_ids)} expired requests")
        
        for request in (db.request_dao.get_request(rid) for rid in expired_ids):
            if not request:
                continue
                
            try:
                # Delete process folder
                folder_path = os.path.join(TEMP_FOLDER, str(request.process_id))
                if os.path.exists(folder_path):
                    shutil.rmtree(folder_path)
                    logger.info(f"Cleaned folder: {folder_path}")
                    
                # Mark as failed in DB
                db.fail_processing(
                    request_id=request.id,
                    details={"reason": "Expired and cleaned"},
                    result_file="",
                    log_file=""
                )
                
            except Exception as cleanup_error:
                logger.error(f"Failed to clean request {request.id}: {str(cleanup_error)}")

    except Exception as e:
        logger.error(f"Error clearing expired requests: {str(e)}")
        raise

async def read_pages(process_id, start_page, parts_to_make=1):
    website = start_page.split("/")[2]
    try:
        parsing_process = resolve_website(website, process_id)
        parsing_process.parse_iterations(start_page, parts_to_make)

    except Exception as e:
        raise Exception(f"Processing failed: {str(e)}")
