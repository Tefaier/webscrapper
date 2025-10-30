from contextlib import asynccontextmanager
import os
import shutil
import logging
from fastapi import FastAPI

from dto.request import Request
from objects.builders.website_resolve import resolve_website
from objects.file_handlers.log_writer import LogWriter
from settings.system_defaults import APPLICATION_LOGS_PATH, DB_PATH, TEMP_FOLDER, MAX_ACTIVE_PROCESSES
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from database import db
from concurrent.futures import ThreadPoolExecutor, as_completed, wait

from utils.web_functions import get_domain

scheduler = BackgroundScheduler()
logger = LogWriter(APPLICATION_LOGS_PATH).get_logger(__name__)
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
        logger.info("Scheduler started")
        yield
    finally:
        logger.info("Shutdown started")
        scheduler.shutdown()
        logger.info("Shutdown of db_executor")
        db_executor.shutdown(wait=True)
        logger.info("Shutdown of executor")
        executor.shutdown(wait=True)
        logger.info("Shutdown finished")


def process_waiting_requests():
    """Process pending requests with parallel execution"""
    try:
        ids = db.get_pending_requests(MAX_ACTIVE_PROCESSES)

        if not ids:
            return

        # Submit DB operations to thread pool
        futures = [db_executor.submit(db.get_request, id) for id in ids]
        task_futures = []

        # Process completed DB futures
        for future in as_completed(futures):
            try:
                request = future.result()
                if request:
                    task_futures.append(executor.submit(read_pages, request))

            except Exception as e:
                logger.error(f"Error getting request: {str(e)}")

        wait(task_futures)

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


def read_pages(request: Request):
    try:
        parsing_process = resolve_website(get_domain(request.url), request)
        result = parsing_process.parse_iterations(request.url, request.chapters)
        if result["success"]:
            logger.debug(f"Finished request with request id {request.request_id} - SUCCESS")
            db.complete_processing(request.id, result)
        else:
            logger.debug(f"Finished request with request id {request.request_id} - FAILED")
            db.fail_processing(request.id, result)

    except Exception as e:
        db.fail_processing(request.id, {})
        logger.error(f"Error while calling running parser: {str(e)}")
