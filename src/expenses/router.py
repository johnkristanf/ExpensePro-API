from fastapi import APIRouter, Depends

from src.expenses.dependencies import get_expense_service
from src.expenses.service import ExpenseService
from src.database import Database
from src.expenses.schemas import ExpenseChatIn

expense_router = APIRouter()


@expense_router.post("/create", status_code=201)
async def create_expense(
    payload: ExpenseChatIn,
    expense_service: ExpenseService = Depends(get_expense_service)
):
    result = await expense_service.agent_expense_insert(payload.message)
    return result
