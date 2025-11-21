from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.agents.prompts import SYSTEM_PROMPT
from src.config import settings

from src.budgets.tools import BudgetsToolFactory
from src.expenses.tools import ExpenseToolFactory
from src.categories.tools import CategoriesToolFactory


class Agent:
    """Main service orchestrating the expense insertion workflow."""

    def __init__(self, session: AsyncSession, current_user_id: int):
        self.current_user_id = current_user_id
        self.expense_tool_factory = ExpenseToolFactory(session, current_user_id)
        self.categories_tool_factory = CategoriesToolFactory(session, current_user_id)
        self.budgets_tool_factory = BudgetsToolFactory(session, current_user_id)

    def load_agent(self):
        """Process user message and create expense using AI agent."""
        model = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=settings.OPENAI_API_KEY,
            temperature=0,
            max_tokens=1500,
            timeout=30,
            streaming=True,
        )

        agent = create_agent(
            model,
            system_prompt=SYSTEM_PROMPT,
            tools=[
                self.expense_tool_factory.create_create_expense_tool,
                self.expense_tool_factory.create_list_expenses_tool,
                
                self.categories_tool_factory.create_get_category_id_tool,
                self.budgets_tool_factory.create_get_budget_id_tool
            ],
            middleware=[
                self.expense_tool_factory.handle_expense_tool_errors,
            ],
        )

        return agent
