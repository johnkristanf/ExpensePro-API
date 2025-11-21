from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.config import settings
from src.expenses.repositories import ExpenseRepository
from src.expenses.tools import ExpenseToolFactory


class ExpenseService:
    """Main service orchestrating the expense insertion workflow."""

    def __init__(self, session: AsyncSession, current_user_id: int):
        self.current_user_id = current_user_id
        self.repository = ExpenseRepository(session)
