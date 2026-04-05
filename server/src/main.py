from contextlib import asynccontextmanager
from fastapi import FastAPI

from api.router import router
from exceptions.handlers import register_exception_handlers
from core.seed_in_memory import seed_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up... Populating seed data...")
    await seed_data()
    yield
    print("Shutting down...")


app = FastAPI(title="Auction Platform", version="1.0.0", lifespan=lifespan)

register_exception_handlers(app)

app.include_router(router, prefix="/api/v1")
