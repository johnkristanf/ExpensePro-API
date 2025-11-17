from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime

from sqlalchemy.orm import relationship
from src.database import Base

from sqlalchemy import ForeignKey
from src.users.models import User

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    spending_type = Column(Text, nullable=True)
    date_spent = Column(DateTime, nullable=True)

    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    budget_id = Column(Integer, ForeignKey("budgets.id"), nullable=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    category = relationship("Category", back_populates="expenses")
    budgets = relationship("Budget", back_populates="expenses")
    user = relationship(User, back_populates="expenses")
