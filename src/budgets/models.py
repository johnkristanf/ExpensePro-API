from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from datetime import datetime
from src.database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    current_amount = Column(Float(precision=2), default=0)
    total_amount = Column(Float(precision=2), nullable=False)
    budget_period = Column(Date, nullable=False)

    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user = relationship("User", back_populates="budgets")

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
