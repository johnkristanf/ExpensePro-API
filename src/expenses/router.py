from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from src.expenses.dependencies import get_expense_service
from src.expenses.service import ExpenseService
from src.expenses.schemas import ExpenseChatIn

expense_router = APIRouter()

