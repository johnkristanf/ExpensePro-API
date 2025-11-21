from pydantic import BaseModel, Field
from typing import Optional

class CategoryIn(BaseModel):
    name: str = Field(..., max_length=255)
    notes: Optional[str] = None
    user_id: int