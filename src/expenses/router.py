from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.expenses.service import ExpenseService
from src.database import Database
from src.expenses.schemas import ExpenseChatIn

expense_router = APIRouter()


@expense_router.post("/create", status_code=200)
async def create_expense(
    payload: ExpenseChatIn,
    session: AsyncSession = Depends(Database.get_async_session),
    # DEPENDENCY INJECT THE FETCHING OF THE CURRENT USER (JWT-BASED)
):
    current_user = {"id": 1, "name": "John Kristan"}

    expense_service = ExpenseService(session, current_user["id"])
    result = await expense_service.agent_expense_insert(payload.message)
    return {"result": result}
