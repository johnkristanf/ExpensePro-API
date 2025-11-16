from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from pydantic.v1.class_validators import validator


class ExpenseChatIn(BaseModel):
    message: str


class ExpenseIn(BaseModel):

    description: str = Field(..., description="Description of the expense")
    amount: float = Field(
        ..., description="The amount of the expense in decimal format"
    )
    spending_type: Optional[str] = Field(
        default=None, description="Type of spending (optional, e.g. leisure, necessity)"
    )
    date_spent: Optional[datetime] = Field(
        default=None, description="Date when the expense was made"
    )
    category_id: Optional[int] = Field(
        default=None, description="ID of the related category (optional)"
    )
    budget_id: Optional[int] = Field(
        default=None, description="ID of the related budget (optional)"
    )
    user_id: int = Field(..., description="ID of the user who made the expense")

    @validator("amount")
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must be positive")
        return round(v, 2)

    @validator("date_spent", pre=True)
    def parse_date_spent(cls, v):
        if isinstance(v, str):
            try:
                return datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("date_spent must be in YYYY-MM-DD format")
        return v
