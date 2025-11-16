from typing import Optional
from src.users.models import User
from sqlalchemy.ext.asyncio import AsyncSession


class UserService:
    @staticmethod
    async def get_user_by_id(
        self, session: AsyncSession, user_id: int
    ) -> Optional[User]:
        return await session.get(User, user_id)
