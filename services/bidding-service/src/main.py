from contextlib import asynccontextmanager
from fastapi import FastAPI

from api.router import router
from exceptions.handlers import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Bidding Service starting up...")
    yield
    print("Bidding Service shutting down...")


app = FastAPI(title="Bidding Service", version="1.0.0", lifespan=lifespan)

register_exception_handlers(app)

app.include_router(router, prefix="/api/v1")
