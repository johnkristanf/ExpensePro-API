from pydantic import BaseModel


class LLMChatIn(BaseModel):
    message: str
