from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.expenses.schemas import ExpenseIn
from src.expenses.models import Expense


class ExpenseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_expense(self, expense_data: ExpenseIn):
        expense = Expense(**expense_data.model_dump())
        self.session.add(expense)
        await self.session.commit()
        await self.session.refresh(expense)
        return expense

    async def list_expenses(self, user_id: int):
        stmt = select(Expense).where(Expense.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
