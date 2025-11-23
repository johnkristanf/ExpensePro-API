from typing import Optional
from langchain_core.tools import StructuredTool
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.budgets.schemas import BudgetIn
from src.budgets.repositories import BudgetRepository


class BudgetsToolFactory:
    """Factory to create tools with injected dependencies."""

    def __init__(self, session: AsyncSession, user_id: int):
        self.repository = BudgetRepository(session)
        self.user_id = user_id

    def all(self):
        return [
            self.get_budget_id_tool(),
            self.create_budget_tool()
        ]

    def create_budget_tool(self) -> StructuredTool:
        """Create create_budget tool with injected dependencies."""

        async def create_budget(
            name: str,
            total_amount: int,
            current_amount: int,
            budget_period: Optional[str] = None,
        ) -> dict:
            """Create a new budget record in the database.

            Args:
                name: Name of the budget.
                total_amount: The total allocated amount for the budget.
                current_amount: The current amount remaining or spent.
                budget_period: The budget period in YYYY-MM-DD format (optional).

            Returns:
                Dictionary with the created category details
            """
            budget_data = BudgetIn(
                name=name,
                total_amount=total_amount,
                current_amount=current_amount,
                budget_period=budget_period,
                user_id=self.user_id
            )

            budget = await self.repository.create_budget(budget_data)

            return {
                "status": "success",
                "budget": {
                    "id": budget.id,
                    "name": budget.name,
                },
            }

        return StructuredTool.from_function(
            coroutine=create_budget,
            name="create_budget",
            description="Create a new categories record in the database",
        )

    def get_budget_id_tool(self) -> StructuredTool:
        """
        Tool for retrieving a budget id by searching for a name (case-insensitive, partial matches allowed).
        """

        async def get_budget_id(name: str) -> int:
            """
            Returns the ID of a category matching the given name (case-insensitive, partial match).

            Args:
                name: The name (or partial name) of the category to search for.

            """
            budget = await self.repository.get_budget_by_name(
                name, user_id=self.user_id
            )
            return budget.id if budget else None

        return StructuredTool.from_function(
            coroutine=get_budget_id,
            name="get_budget_id",
            description="Get the ID of a budget by name (case-insensitive, partial match allowed).",
        )
