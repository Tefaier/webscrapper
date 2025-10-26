from contextlib import asynccontextmanager

from fastapi import FastAPI
from objects.builders.website_resolve import resolve_website
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

scheduler = AsyncIOScheduler()

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
    pass

async def clear_expired_requests():
    pass

async def read_pages(process_id, start_page, parts_to_make=1):
    website = start_page.split("/")[2]
    try:
        parsing_process = resolve_website(website, process_id)
        parsing_process.parse_iterations(start_page, parts_to_make)

    except Exception as e:
        raise Exception(f"Processing failed: {str(e)}")
