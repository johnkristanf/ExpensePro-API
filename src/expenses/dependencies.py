from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import Database
from src.expenses.service import ExpenseService

# Dependency that accepts arguments from other dependencies
async def get_expense_service(
    session: AsyncSession = Depends(Database.get_async_session),
    current_user: dict = Depends(lambda: {"id": 1, "name": "John Kristan"}),  # Example user
) -> ExpenseService:
    return ExpenseService(session, current_user["id"])
