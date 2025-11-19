from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.prompts import expense_system_prompt
from src.config import settings
from src.expenses.repositories import ExpenseRepository
from src.expenses.tools import ExpenseToolFactory


class ExpenseService:
    """Main service orchestrating the expense insertion workflow."""

    def __init__(self, session: AsyncSession, current_user_id: int):
        self.current_user_id = current_user_id
        self.repository = ExpenseRepository(session)
        self.tool_factory = ExpenseToolFactory(self.repository, current_user_id)

    async def agent_expense_insert(self, user_message: str) -> dict:
        """Process user message and create expense using AI agent."""
        model = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=settings.OPENAI_API_KEY,
            temperature=0,
            max_tokens=1500, 
            timeout=30, 
            streaming=True
        )

        agent = create_agent(
            model,
            system_prompt=expense_system_prompt(),
            tools=self.tool_factory.expense_create_tools(),
            middleware=[self.tool_factory.handle_expense_tool_errors],
        )
        
        result = await agent.astream_events(
            {"messages": [{"role": "user", "content": user_message}]}
        )

        return result
