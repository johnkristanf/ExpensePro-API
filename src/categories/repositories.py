from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.categories.models import Category
from src.categories.schemas import CategoryIn

class CategoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_category_by_name(self, category_name: str, user_id: int):
        stmt = select(Category).where(
            Category.name.ilike(f"%{category_name}%"),
            Category.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_category(self, category_data: CategoryIn, user_id: int):
        category = Category(**category_data.model_dump(), user_id=user_id)
        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category)
        return category

    async def list_categories(self, user_id: int):
        stmt = select(Category).where(Category.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_category_by_id(self, category_id: int, user_id: int):
        stmt = select(Category).where(
            Category.id == category_id,
            Category.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

