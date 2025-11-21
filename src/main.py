from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

from src.agents.router import agent_router
from src.database import Database
from src.utils import group


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    Database.connect()
    yield
    await Database.close()


api_v1_router = group(
    "/api/v1",
    (agent_router, "/agent", ["Agent"]),
)

app.include_router(api_v1_router)

@app.get("/health")
def health():
    return {"message": "Server is Healthy"}
