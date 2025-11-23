from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.budgets.schemas import BudgetIn
from src.budgets.models import Budget


class BudgetRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_budget_by_name(self, budget_name: str, user_id: int):
        stmt = select(Budget).where(
            Budget.name.ilike(f"%{budget_name}%"), Budget.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_budget(self, budget_data: BudgetIn, user_id: int):
        budget = Budget(**budget_data.model_dump())
        self.session.add(budget)
        await self.session.commit()
        await self.session.refresh(budget)
        return budget

    async def list_budgets(self, user_id: int):
        stmt = select(Budget).where(Budget.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_budget_by_id(self, budget_id: int, user_id: int):
        stmt = select(Budget).where(Budget.id == budget_id, Budget.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
