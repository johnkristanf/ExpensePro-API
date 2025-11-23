from fastapi import Depends
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.database import Database
from src.agents.agent import Agent


def get_agent(
    session: AsyncSession = Depends(Database.get_async_session),
    user: dict = Depends(lambda: {"id": 1, "name": "John Kristan"}),
):
    """FastAPI dependency that provides an Agent instance."""
    return Agent(session, user["id"])
