
from pydantic import BaseModel


class AgentChatIn(BaseModel):
    message: str