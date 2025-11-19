from datetime import datetime
from typing import Optional
from langchain.agents.middleware import wrap_tool_call
from langchain_core.messages import ToolMessage
from langchain_core.tools import StructuredTool

from src.expenses.schemas import ExpenseIn
from src.expenses.repositories import ExpenseRepository


class ExpenseToolFactory:
    """Factory to create tools with injected dependencies."""

    def __init__(self, repository: ExpenseRepository, user_id: int):
        self.repository = repository
        self.user_id = user_id

    @wrap_tool_call
    async def handle_expense_tool_errors(request, handler):
        """Handle tool execution errors with custom messages."""
        try:
            return await handler(request)
        except Exception as e:
            return ToolMessage(
                content=f"Tool error: {str(e)}",
                tool_call_id=request.tool_call["id"],
            )

    def create_get_category_id_tool(self) -> StructuredTool:
        """Create get_category_id tool with injected dependencies."""

        async def get_category_id(category_name: str) -> dict:
            """Look up the category ID by category name.

            Args:
                category_name: The name of the category to find

            Returns:
                Dictionary with category_id and category_name, or None if not found
            """
            category = await self.repository.get_category_by_name(category_name, self.user_id)

            if category:
                return {
                    "category_id": category.id,
                    "category_name": category.name,
                    "found": True,
                }
            return {
                "category_id": None,
                "category_name": category_name,
                "found": False,
                "message": f"Category '{category_name}' not found",
            }

        return StructuredTool.from_function(
            coroutine=get_category_id,
            name="get_category_id",
            description="Look up the category ID by category name",
        )

    def create_get_budget_id_tool(self) -> StructuredTool:
        """Create get_budget_id tool with injected dependencies."""
        repo = self.repository
        user_id = self.user_id

        async def get_budget_id(budget_name: str) -> dict:
            """Look up the budget ID by budget name.

            Args:
                budget_name: The name of the budget to find

            Returns:
                Dictionary with budget_id and budget_name, or None if not found
            """
            budget = await repo.get_budget_by_name(budget_name, user_id)

            if budget:
                return {
                    "budget_id": budget.id,
                    "budget_name": budget.name,
                    "found": True,
                }
            return {
                "budget_id": None,
                "budget_name": budget_name,
                "found": False,
                "message": f"Budget '{budget_name}' not found",
            }

        return StructuredTool.from_function(
            coroutine=get_budget_id,
            name="get_budget_id",
            description="Look up the budget ID by budget name",
        )

    def create_list_categories_tool(self) -> StructuredTool:
        """Create list_categories tool with injected dependencies."""

        async def list_categories() -> dict:
            """Get all available categories for the current user.

            Returns:
                Dictionary with list of categories
            """
            categories = await self.repository.list_categories(self.user_id)

            return {
                "categories": [{"id": cat.id, "name": cat.name} for cat in categories],
                "count": len(categories),
            }

        return StructuredTool.from_function(
            coroutine=list_categories,
            name="list_categories",
            description="Get all available categories for the current user",
        )

    def create_list_budgets_tool(self) -> StructuredTool:
        """Create list_budgets tool with injected dependencies."""

        async def list_budgets() -> dict:
            """Get all available budgets for the current user.

            Returns:
                Dictionary with list of budgets
            """
            budgets = await self.repository.list_budgets(self.user_id)

            return {
                "budgets": [
                    {"id": b.id, "name": b.name, "amount": getattr(b, "amount", None)}
                    for b in budgets
                ],
                "count": len(budgets),
            }

        return StructuredTool.from_function(
            coroutine=list_budgets,
            name="list_budgets",
            description="Get all available budgets for the current user",
        )

    def create_create_expense_tool(self) -> StructuredTool:
        """Create create_expense tool with injected dependencies."""

        async def create_expense(
            description: str,
            amount: float,
            category_id: Optional[int] = None,
            budget_id: Optional[int] = None,
            spending_type: Optional[str] = None,
            date_spent: Optional[str] = None,
        ) -> dict:
            """Create a new expense record in the database.

            Args:
                description: Description of the expense
                amount: The monetary amount of the expense
                spending_type: Type of spending (wants, needs, etc.)
                date_spent: Date in YYYY-MM-DD format, defaults to today
                category_id: The ID of the category (use get_category_id first)
                budget_id: The ID of the budget (use get_budget_id first)

            Returns:
                Dictionary with the created expense details
            """
            # Parse date if provided
            parsed_date = None
            if date_spent:
                try:
                    parsed_date = datetime.strptime(date_spent, "%Y-%m-%d")
                except ValueError:
                    return {
                        "status": "error",
                        "message": "Invalid date format. Use YYYY-MM-DD",
                    }

            expense_data = ExpenseIn(
                description=description,
                amount=amount,
                spending_type=spending_type,
                date_spent=parsed_date or datetime.now(),
                category_id=category_id,
                budget_id=budget_id,
                user_id=self.user_id,
            )

            expense = await self.repository.create_expense(expense_data)

            return {
                "status": "success",
                "expense": {
                    "id": expense.id,
                    "description": expense.description,
                    "amount": float(expense.amount),
                    "category_id": expense.category_id,
                    "budget_id": expense.budget_id,
                    "spending_type": expense.spending_type,
                    "date_spent": (
                        expense.date_spent.isoformat() if expense.date_spent else None
                    ),
                    "user_id": expense.user_id,
                },
            }

        return StructuredTool.from_function(
            coroutine=create_expense,
            name="create_expense",
            description="Create a new expense record in the database",
        )
        
    def create_list_expenses_tool(self):
        async def list_expenses():
            expenses = await self.repository.list_expenses(self.user_id)
            return {
                "status": "success",
                "data": [
                    {
                        "id": e.id,
                        "description": e.description,
                        "amount": float(e.amount),
                        "category_id": e.category_id,
                        "budget_id": e.budget_id,
                        "date_spent": e.date_spent.isoformat() if e.date_spent else None,
                    } for e in expenses
                ]
            }

        return StructuredTool.from_function(
            coroutine=list_expenses,
            name="list_expenses",
            description="Get a list of all expenses for the current user"
        )

    def expense_create_tools(self) -> list:
        """Create all tools with injected dependencies."""
        return [
            self.create_get_category_id_tool(),
            self.create_get_budget_id_tool(),
            self.create_create_expense_tool(),
            self.create_list_expenses_tool()
        ]
