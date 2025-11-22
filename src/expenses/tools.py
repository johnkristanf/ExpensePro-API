from datetime import datetime
from typing import Optional
from langchain.agents.middleware import wrap_tool_call
from langchain_core.messages import ToolMessage
from langchain_core.tools import StructuredTool
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.expenses.schemas import ExpenseIn
from src.expenses.repositories import ExpenseRepository


class ExpenseToolFactory:
    """Factory to create tools with injected dependencies."""

    def __init__(self, session: AsyncSession, user_id: int):
        self.repository = ExpenseRepository(session)
        self.user_id = user_id
        
    def all(self):
        return [
            self.create_expense_tool(),
            self.list_expenses_tool(),
        ]

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

    def create_expense_tool(self) -> StructuredTool:
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

    def list_expenses_tool(self):
        """Create the list_expenses tool for the agent."""

        async def list_expenses():
            """
            This tool allows the agent to retrieve all expenses for the current user in the system.

            Returns a list of expense records, each containing:
                - id: the unique ID of the expense
                - description: what the expense is for
                - amount: amount spent (as float)
                - category_id: associated category ID or None
                - budget_id: associated budget ID or None
                - date_spent: ISO8601 date string or None if not set

            Returns:
               The detailed list of all expenses
            """
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
                        "date_spent": (
                            e.date_spent.isoformat() if e.date_spent else None
                        ),
                    }
                    for e in expenses
                ],
            }

        return StructuredTool.from_function(
            coroutine=list_expenses,
            name="list_expenses",
            description="Retrieve all expense records for the current user. Each record includes: id, description, amount, category_id, budget_id, and date_spent (ISO8601).",
        )
