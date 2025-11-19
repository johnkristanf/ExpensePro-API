from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.expenses.schemas import ExpenseIn
from src.expenses.models import Expense

from src.categories.models import Category
from src.budgets.models import Budget


class ExpenseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_category_by_name(self, category_name: str, user_id: int):
        stmt = select(Category).where(
            Category.name.ilike(f"%{category_name}%"), Category.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_budget_by_name(self, budget_name: str, user_id: int):
        stmt = select(Budget).where(
            Budget.name.ilike(f"%{budget_name}%"), Budget.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_categories(self, user_id: int):
        stmt = select(Category).where(Category.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_budgets(self, user_id: int):
        stmt = select(Budget).where(Budget.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

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