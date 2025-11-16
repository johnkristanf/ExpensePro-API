from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import Database
from src.expenses.service import ExpenseService


async def get_expense_service() -> ExpenseService:
    return ExpenseService
