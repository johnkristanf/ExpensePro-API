from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.config import settings
from src.database import Database
import os

db = Database(dsn=settings.DATABASE_ASYNC_DSN)
app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()
    yield
    await db.close()


@app.get("/health")
def health():
    return {"message": "Server is Healthy"}
