from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.expenses.schemas import LLMChatIn

router = APIRouter()


@router.post("/chat")
async def llm_chat(payload: LLMChatIn):
    return JSONResponse({"echo": payload.model_dump()})
