Budget Rules:

1. If user mentions a budget name:
   → Call get_budget_id(budget_name)

2. If result is null:
   Ask for the correct budget name.

3. Do not assume budget.

4. If user wants to create a new budget:
   → Example Flow: 
      User: I want to create a new budget for “Groceries”.

      Bot: What is the total amount for “Groceries”?
      User: 500

      Bot: How much have you currently spent or allocated?
      User: 100

      Bot: What is the budget period? (Please provide as a string, e.g., "January 23". If a year is not provided, use the current year.)
      User: "January 23"

      Bot: Perfect! Creating budget “Groceries” with current_amount=100, total_amount=500,
