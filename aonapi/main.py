from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from contextlib import asynccontextmanager
from aonapi.indexer import update_categories_and_uuids
from aonapi.settings import setup_logging

setup_logging()
import logging

logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
scheduler = AsyncIOScheduler()


# This is a context manager that will run when the app starts up and shut down.
@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_event()
    yield
    pass


# This is the main FastAPI app.
app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="aonapi/templates")

from aonapi.routes.nethys_data import router as nethys_data_router

app.include_router(nethys_data_router)


# These are the routes for the app.
@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "message": "Hello World!"}
    )


# This is the event that will run when the app starts up.
async def startup_event():
    print("Starting up...")
    update_categories_and_uuids()  # Initial update
    scheduler.add_job(
        update_categories_and_uuids, trigger=IntervalTrigger(seconds=1800)
    )  # Run every 30 minutes
    scheduler.start()
