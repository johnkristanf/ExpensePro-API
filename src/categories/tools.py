from typing import Optional
from langchain_core.tools import StructuredTool
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.categories.schemas import CategoryIn
from src.categories.repositories import CategoryRepository


class CategoriesToolFactory:
    """Factory to create tools with injected dependencies."""

    def __init__(self, session: AsyncSession, user_id: int):
        self.repository = CategoryRepository(session)
        self.user_id = user_id

    def all(self):
        return [self.get_category_id_tool(), self.create_category_tool()]

    def create_category_tool(self) -> StructuredTool:
        """Create create_category tool with injected dependencies."""

        async def create_category(
            name: str,
            notes: Optional[str] = None,
        ) -> dict:
            """Create a new expense record in the database.

            Args:
                name: Name of the category
                notes: Simple notes for the category
            Returns:
                Dictionary with the created category details
            """
            category_data = CategoryIn(name=name, notes=notes, user_id=self.user_id)

            category = await self.repository.create_category(category_data)

            return {
                "status": "success",
                "category": {
                    "id": category.id,
                    "name": category.name,
                },
            }

        return StructuredTool.from_function(
            coroutine=create_category,
            name="create_category",
            description="Create a new categories record in the database",
        )

    def get_category_id_tool(self) -> StructuredTool:
        """
        Tool for retrieving a category id by searching for a name (case-insensitive, partial matches allowed).
        """

        async def get_category_id(name: str) -> int:
            """
            Returns the ID of a category matching the given name (case-insensitive, partial match), or None if not found.
            """
            category = await self.repository.get_category_by_name(
                name, user_id=self.user_id
            )
            return category.id if category else None

        return StructuredTool.from_function(
            coroutine=get_category_id,
            name="get_category_id",
            description=(
                "Get the ID of a category by name (case-insensitive, partial match allowed). "
                "Returns just the integer category_id, or None if not found."
            ),
        )
