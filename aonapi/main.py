from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from contextlib import asynccontextmanager
from aonapi.indexer import update_categories_and_uuids


scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_event()
    yield
    pass


app = FastAPI(lifespan=lifespan)

templates = Jinja2Templates(directory="aonapi/templates")


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "message": "Hello World!"}
    )


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


async def startup_event():
    print("Starting up...")
    update_categories_and_uuids()  # Initial update
    scheduler.add_job(
        update_categories_and_uuids, trigger=IntervalTrigger(seconds=1800)
    )  # Run every 30 minutes
    scheduler.start()
