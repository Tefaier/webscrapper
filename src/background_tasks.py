from contextlib import asynccontextmanager
import os
import shutil
import logging
from fastapi import FastAPI

from objects.builders.website_resolve import resolve_website
from settings.system_defaults import DB_PATH, TEMP_FOLDER, MAX_ACTIVE_PROCESSES
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from database import db
from concurrent.futures import ThreadPoolExecutor, as_completed, wait

scheduler = BackgroundScheduler()
logger = logging.getLogger(__name__)
db_executor = ThreadPoolExecutor(max_workers=MAX_ACTIVE_PROCESSES)
executor = ThreadPoolExecutor(max_workers=MAX_ACTIVE_PROCESSES)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        scheduler.add_job(
            process_waiting_requests,
            trigger=IntervalTrigger(minutes=1),
            id="process_waiting_requests",
            replace_existing=True,
        )
        scheduler.add_job(
            clear_expired_requests, trigger=IntervalTrigger(hours=1), id="clear_expired_requests", replace_existing=True
        )
        scheduler.start()
        yield
    finally:
        scheduler.shutdown()
        db_executor.shutdown(wait=True)
        executor.shutdown(wait=True)


def process_waiting_requests():
    """Process pending requests with parallel execution"""
    try:
        ids = db.get_pending_requests(MAX_ACTIVE_PROCESSES)

        if not ids:
            return

        # Submit DB operations to thread pool
        futures = [db_executor.submit(db.get_request, id) for id in ids]

        # Process completed DB futures
        for future in as_completed(futures):
            try:
                request = future.result()
                if request:
                    executor.submit(read_pages, request.request_id, request.url, request.chapters)
            except Exception as e:
                logger.error(f"Error getting request: {str(e)}")

    except Exception as e:
        logger.error(f"Error processing requests: {str(e)}")


def clear_expired_requests():
    """Clean up expired requests and their storage folders"""
    try:
        expired_ids = db.get_expired_requests()

        if not expired_ids:
            return

        cleanup_futures = []
        for id in expired_ids:
            # Submit cleanup tasks to thread pool
            future = executor.submit(clean_single_request, id)
            cleanup_futures.append(future)

        wait(cleanup_futures)

    except Exception as e:
        logger.error(f"Error in clear_expired_requests: {str(e)}")

def clean_single_request(id: int):
    """Clean up a single expired request"""
    try:
        request = db.get_request(id)
        if not request:
            return

        folder_path = os.path.join(TEMP_FOLDER, str(request.request_id))
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)

        logger.info(f"Cleaned up request {id}")

    except Exception as e:
        logger.error(f"Error cleaning request {id}: {str(e)}")


def read_pages(request_id, start_page, parts_to_make=1):
    website = start_page.split("/")[2]
    try:
        parsing_process = resolve_website(website, request_id)
        result = parsing_process.parse_iterations(start_page, parts_to_make)
        if result["success"]:
            db.complete_processing(request_id, result)
        else:
            db.fail_processing(request_id, result)

    except Exception as e:
        db.fail_processing(request_id, {})
        logger.error(f"Error while calling running parser: {str(e)}")
