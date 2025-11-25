# ============= DOMAIN AGENTS =============

# Budget Agent - Focused, small state
class BudgetState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    budget_name: Optional[str]
    budget_amount: Optional[float]
    budget_period: Optional[str]

budget_agent = create_agent(
    model="gpt-4o-mini",
    system_prompt="""You are a budget management specialist.
    Workflows:
    1. Ask for budget name
    2. Ask for total amount
    3. Ask for period
    4. Create budget
    """,
    tools=[
        create_budget,
        list_budgets,
    ],
    state_schema=BudgetState,
    checkpointer=InMemorySaver(),
)

# Expense Agent - Focused, small state
class ExpenseState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    expense_description: Optional[str]
    expense_amount: Optional[float]
    category_id: Optional[str]
    budget_id: Optional[str]

expense_agent = create_agent(
    model="gpt-4o-mini",
    system_prompt="""You are an expense tracking specialist.
    Workflows:
    1. Ask for expense description
    2. Ask for amount
    3. Ask for category
    4. Ask for budget
    5. Create expense
    """,
    tools=[
        create_expense,
        list_categories,
        list_budgets,
    ],
    state_schema=ExpenseState,
    checkpointer=InMemorySaver(),
)

# Income Agent - Focused, small state
class IncomeState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    income_source: Optional[str]
    income_amount: Optional[float]
    income_date: Optional[str]

income_agent = create_agent(
    model="gpt-4o-mini",
    system_prompt="You are an income tracking specialist.",
    tools=[create_income, list_income],
    state_schema=IncomeState,
    checkpointer=InMemorySaver(),
)

# ============= SUPERVISOR AGENT =============

@tool
def route_to_budget_agent(query: str, runtime: ToolRuntime) -> str:
    """Handle budget-related requests"""
    result = budget_agent.invoke({
        "messages": [HumanMessage(content=query)]
    }, config={"configurable": {"thread_id": runtime.context.user_id}})
    return result["messages"][-1].content

@tool
def route_to_expense_agent(query: str, runtime: ToolRuntime) -> str:
    """Handle expense-related requests"""
    result = expense_agent.invoke({
        "messages": [HumanMessage(content=query)]
    }, config={"configurable": {"thread_id": runtime.context.user_id}})
    return result["messages"][-1].content

@tool
def route_to_income_agent(query: str, runtime: ToolRuntime) -> str:
    """Handle income-related requests"""
    result = income_agent.invoke({
        "messages": [HumanMessage(content=query)]
    }, config={"configurable": {"thread_id": runtime.context.user_id}})
    return result["messages"][-1].content

class SupervisorState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

supervisor_agent = create_agent(
    model="gpt-4o",
    system_prompt="""You are a financial assistant router.

Understanding user intent:
- "budget", "create budget" → route_to_budget_agent
- "expense", "add expense" → route_to_expense_agent
- "income", "earning" → route_to_income_agent
- "report", "summary" → route_to_reports_agent

Always delegate domain-specific requests to the appropriate specialist agent.
Provide the user's full query as-is to the agent you route to.
""",
    tools=[
        route_to_budget_agent,
        route_to_expense_agent,
        route_to_income_agent,
    ],
    state_schema=SupervisorState,
    checkpointer=InMemorySaver(),
)


# User: "Add November Transportation Budget"
# ↓
# Supervisor reads: "budget" keyword
# Supervisor routes: "Add November Transportation Budget" → budget_agent
# ↓
# Budget Agent gets fresh conversation:
# - State is small: {messages, budget_name, budget_amount, budget_period}
# - Prompt is focused: "You are a budget specialist"
# - Tools are 3 not 30
# ↓
# Budget Agent asks: "What is the total amount?"
# User: "10000"
# Budget Agent: "What is the period?"
# User: "November 2024"
# Budget Agent: Creates budget ✅
# ↓
# Supervisor gets result back and relays to user