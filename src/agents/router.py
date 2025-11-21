from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from src.agents.dependencies import get_agent
from src.agents.schemas import AgentChatIn
from src.agents.agent import Agent

agent_router = APIRouter()



@agent_router.post("/chat", status_code=201)
async def agent_chat(
    payload: AgentChatIn,
    agent: Agent = Depends(get_agent),
):
    loaded_agent = agent.load_agent()

    async def stream():
        async for event in loaded_agent.astream_events(
            {"messages": [{"role": "user", "content": payload.message}]},
            version="v2",
        ):
            if event["event"] == "on_chat_model_stream":
                print(f"DATA CHUNK: {event['data']['chunk']}")
                token = event["data"]["chunk"].content
                if token:
                    yield token

        yield "[END]"

    return StreamingResponse(stream(), media_type="text/plain")
