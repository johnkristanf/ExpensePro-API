from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

from src.expenses.router import expense_router
from src.database import Database
from src.utils import group

from src.expenses.router import expense_router

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
    (expense_router, "/expense", ["Expense"]),
)

app.include_router(api_v1_router)

@app.get("/health")
def health():
    return {"message": "Server is Healthy"}
