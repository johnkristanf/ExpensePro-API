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
        self.tool_factory = ExpenseToolFactory(self.repository, current_user_id)
        
        
    async def agent_expense_insert(self, user_message: str) -> dict:
        """Process user message and create expense using AI agent."""
        model = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=settings.OPENAI_API_KEY,
            temperature=0,
            max_tokens=1500,  # Reduced for faster responses
            timeout=30,  # Reduced timeout
        )

        # OPTIMIZED: More concise, directive system prompt
        system_prompt = """You are an expense tracking assistant. Extract expense details and create records efficiently.

CRITICAL: Only call tools when absolutely necessary. Follow these rules:

1. ALWAYS extract: description, amount
2. For category: 
   - If user mentions a category name → call get_category_id(category_name) ONCE
   - If category not found or not mentioned → set category_id=None
   - NEVER call list_categories unless user explicitly asks "what categories do I have?"
   
3. For budget:
   - If user mentions a budget name → call get_budget_id(budget_name) ONCE  
   - If budget not found or not mentioned → set budget_id=None
   - NEVER call list_budgets unless user explicitly asks "what budgets do I have?"

4. Infer spending_type: "leisure" or "necessity" from context
5. Extract date_spent if mentioned (YYYY-MM-DD), otherwise omit

Then immediately call create_expense with extracted data.

EXAMPLES (showing ONLY necessary tool calls):

"I spent $45 on groceries"
→ get_category_id("groceries")  # Only if you think "groceries" might match a category
→ create_expense(description="groceries", amount=45, category_id=X, spending_type="necessity")

"Paid $120 for concert tickets"  
→ create_expense(description="concert tickets", amount=120, spending_type="leisure")
# NO category/budget lookup needed - user didn't mention any

"$50 for dinner from my food budget"
→ get_budget_id("food")  # User explicitly mentioned "food budget"
→ create_expense(description="dinner", amount=50, budget_id=X, spending_type="necessity")

BE EFFICIENT: Minimize tool calls. Create the expense as quickly as possible."""

        # Get tools with injected dependencies
        tools = self.tool_factory.expense_create_tools()
        
        agent = create_agent(
            model,
            system_prompt=system_prompt,
            tools=tools,
            middleware=[self.tool_factory.handle_expense_tool_errors],
        )

        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": user_message}]}
        )

        return result

#     async def agent_expense_insert(self, user_message: str) -> dict:
#         """Process user message and create expense using AI agent."""
#         model = ChatOpenAI(
#             model="gpt-4o-mini",
#             api_key=settings.OPENAI_API_KEY,
#             temperature=0,
#             max_tokens=1500,
#             timeout=30,
#         )

#         system_prompt = """You are an expense tracking assistant. Your job is to:

# 1. Extract expense information from user messages
# 2. Look up category and budget IDs if mentioned
# 3. Create the expense record with all relevant information

# WORKFLOW:
# 1. If user mentions a category (e.g., "food", "groceries", "dining"):
#    - First call list_categories to see available categories
#    - Then call get_category_id with the category name to get its ID
   
# 2. If user mentions a budget (e.g., "monthly budget", "vacation fund"):
#    - First call list_budgets to see available budgets
#    - Then call get_budget_id with the budget name to get its ID

# 3. After getting IDs (or determining they're not needed), call create_expense with:
#    - description: clear description of the expense
#    - amount: numeric value
#    - category_id: ID from step 1 (if found)
#    - budget_id: ID from step 2 (if found)
#    - spending_type: "leisure" or "necessity" (infer from context)
#    - date_spent: in YYYY-MM-DD format (if mentioned, otherwise omit for today)

# EXAMPLES:
# User: "I spent $45 on groceries"
# → 1. list_categories()
# → 2. get_category_id("groceries") or get_category_id("food")
# → 3. create_expense(description="groceries", amount=45, category_id=X, spending_type="necessity")

# User: "Paid $120 for concert tickets from my entertainment budget"
# → 1. list_budgets()
# → 2. get_budget_id("entertainment")
# → 3. create_expense(description="concert tickets", amount=120, budget_id=Y, spending_type="leisure")

# User: "Netflix subscription 15.99"
# → create_expense(description="Netflix subscription", amount=15.99, spending_type="leisure")

# """
#         # Get tools with injected dependencies
#         tools = self.tool_factory.create_all_tools()
#         agent = create_agent(
#             model,
#             system_prompt=system_prompt,
#             tools=tools,
#             middleware=[self.tool_factory.handle_expense_tool_errors],
#         )

#         result = await agent.ainvoke(
#             {"messages": [{"role": "user", "content": user_message}]}
#         )

#         return result


