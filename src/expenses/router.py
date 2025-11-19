import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from src.expenses.dependencies import get_expense_service
from src.expenses.service import ExpenseService
from src.database import Database
from src.expenses.schemas import ExpenseChatIn

expense_router = APIRouter()


@expense_router.post("/chat", status_code=201)
async def create_expense(
    payload: ExpenseChatIn,
    expense_service: ExpenseService = Depends(get_expense_service),
):
    async def stream():
        agent = await expense_service.agent_expense_insert()
        chain_of_thought = []

        async for event in agent.astream_events(
            {"messages": [{"role": "user", "content": payload.message}]},
            version="v2",
        ):

            print(f"EVENTS: {event["event"]}")
            if event['event'] == "on_chat_model_stream":
                print(f"DATA CHUNK: {event['data']['chunk']}")
                token = event['data']['chunk'].content
                if token:
                    yield token


        yield "[END]"

    return StreamingResponse(stream(), media_type="text/plain")
