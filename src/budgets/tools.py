from langchain_core.tools import StructuredTool
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.budgets.repositories import BudgetRepository


class BudgetsToolFactory:
    """Factory to create tools with injected dependencies."""

    def __init__(self, session: AsyncSession, user_id: int):
        self.repository = BudgetRepository(session)
        self.user_id = user_id

    # def create_create_budget_tool(self) -> StructuredTool:
    #     """Create create_budget tool with injected dependencies."""

    #     async def create_budget(
    #         name: str,
    #         notes: Optional[str] = None,
    #     ) -> dict:
    #         """Create a new expense record in the database.

    #         Args:
    #             name: Name of the category
    #             notes: Simple notes for the category
    #         Returns:
    #             Dictionary with the created category details
    #         """
    #         category_data = CategoryIn(
    #             name=name,
    #             notes=notes,
    #             user_id=self.user_id,
    #         )

    #         category = await self.repository.create_budget(category_data)

    #         return {
    #             "status": "success",
    #             "category": {
    #                 "id": category.id,
    #                 "name": category.name,
    #                 "notes": category.notes,
    #                 "user_id": category.user_id,
    #             },
    #         }

    #     return StructuredTool.from_function(
    #         coroutine=create_budget,
    #         name="create_budget",
    #         description="Create a new categories record in the database",
    #     )

    def create_get_budget_id_tool(self) -> StructuredTool:
        """
        Tool for retrieving a budget id by searching for a name (case-insensitive, partial matches allowed).
        """

        async def get_budget_id(budget_name: str) -> dict:
            """
            Returns the ID of a category matching the given name (case-insensitive, partial match).

            Args:
                budget_name: The name (or partial name) of the category to search for.

            """
            category = await self.repository.get_budget_by_name(
                budget_name, user_id=self.user_id
            )
            if category:
                return {"category_id": category.id, "matched_name": category.name}
            else:
                return {"category_id": None, "matched_name": None}

        return StructuredTool.from_function(
            coroutine=get_budget_id,
            name="get_budget_id",
            description="Get the ID of a category by name (case-insensitive, partial match allowed). Returns category_id and matched_name or None if not found.",
            args_schema=None,
        )
