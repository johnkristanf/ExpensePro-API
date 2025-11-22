from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class BudgetIn(BaseModel):
    name: str
    total_amount: float
    budget_period: date
    user_id: int
    current_amount: Optional[float] = 0
