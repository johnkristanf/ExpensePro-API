from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore

from sqlalchemy.ext.asyncio.session import AsyncSession

from src.config import settings

from src.budgets.tools import BudgetsToolFactory
from src.expenses.tools import ExpenseToolFactory
from src.categories.tools import CategoriesToolFactory
from src.utils import load_prompt


class Agent:
    """Main service orchestrating the expense insertion workflow."""

    def __init__(self, session: AsyncSession, user_id: int):
        self.session = session
        self.user_id = user_id

    async def load_agent(self):
        """Process user message and process expense-related operations using AI agent."""
        model = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=settings.OPENAI_API_KEY,
            temperature=0,
            max_tokens=1500,
            timeout=30,
            streaming=True,
        )

        system_prompt = load_prompt(
            "base.md",
            "expense_rules.md",
            "category_rules.md",
            "budget_rules.md",
            "html_rendering.md",
        )

        tools = [
            *ExpenseToolFactory(self.session, self.user_id).all(),
            *CategoriesToolFactory(self.session, self.user_id).all(),
            *BudgetsToolFactory(self.session, self.user_id).all(),
        ]
        
        checkpointer = PostgresSaver(
            conn="postgresql://postgres:admin123@172.17.0.2:5432/expensepro"
        )
        store = PostgresStore(
            conn="postgresql://postgres:admin123@172.17.0.2:5432/expensepro"
        )

        agent = create_agent(
            model,
            system_prompt=system_prompt,
            tools=tools,
            # middleware=[],
            # checkpointer=checkpointer,
        )

        agent_with_memory = agent.compile(checkpointer=checkpointer, store=store)
        return agent_with_memory
