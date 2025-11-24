import json
import logging
from collections import defaultdict
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessageChunk, HumanMessage

from src.agents.dependencies import get_agent
from src.agents.schemas import AgentChatIn
from src.agents.agent import Agent

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

agent_router = APIRouter()


@agent_router.post("/chat", status_code=201)
async def agent_chat(
    payload: AgentChatIn,
    agent: Agent = Depends(get_agent),
):
    loaded_agent = agent.load_agent()
    MAX_TOOL_DEPTH = 10

    async def stream():
        tool_stack = []
        tool_counter = {}

        async for event in loaded_agent.astream_events(
            {"messages": [HumanMessage(content=payload.message)]},
            version="v2",
        ):
            if event["event"] == "on_tool_start":
                tool = event["name"]
                tool_stack.append(tool)
                tool_counter[tool] = tool_counter.get(tool, 0) + 1

                # Prevent deep recursion or excessive repeated tool invocations
                if tool_counter[tool] > MAX_TOOL_DEPTH:
                    yield f"\n❌ TOOL RECURSION ERROR: Tool '{tool}' called too many times, possible infinite loop detected.\n"
                    break

            if event["event"] == "on_tool_end":
                tool = event["name"]
                if tool_stack and tool_stack[-1] == tool:
                    tool_stack.pop()
                else:
                    if tool in tool_stack:
                        tool_stack.remove(tool)

            if event["event"] == "on_tool_error":
                tool = event["name"]
                error = event["data"]["error"]
                print("\n❌ TOOL ERROR")
                print(f"Tool: {tool}")
                print(f"Error: {error}\n")

            if event["event"] == "on_chat_model_stream":
                chunk = event["data"]["chunk"].content
                if chunk:
                    yield chunk

        yield "[END]"

    return StreamingResponse(stream(), media_type="text/plain")
