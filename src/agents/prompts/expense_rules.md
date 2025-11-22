Expense Processing Rules:

1. Always extract:
   - description
   - amount

2. Infer spending_type as "needs" or "wants".

3. Extract date if mentioned.

4. Never call create_expense until category_id AND budget_id are known.

5. If user didn't mention a category:
   Ask: "Which category should this expense belong to?"

6. If user didn't mention a budget:
   Ask: "Which budget should this expense be assigned to?"
