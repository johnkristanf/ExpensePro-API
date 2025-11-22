import json
import logging
from collections import defaultdict
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from src.agents.dependencies import get_agent
from src.agents.schemas import AgentChatIn
from src.agents.agent import Agent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
            print(f"EVENT DATA: {event}")
            # -----------------------------
            # LOG TOOL START
            # -----------------------------
            if event["event"] == "on_tool_start":
                tool = event["name"]
                # print(f"EVENT START TOOL DATA : {event['data']}")
                # logger.info("🔧 TOOL START\nTool: %s\nArgs: %s", tool, json.dumps(tool_result, indent=2, default=str))

            # -----------------------------
            # LOG TOOL END
            # -----------------------------
            if event["event"] == "on_tool_end":
                tool = event["name"]
                # print(f"EVENT END TOOL DATA : {event['data']}")
                # logger.info("✅ TOOL END\nTool: %s\nOutput: %s", tool, json.dumps(tool_result, indent=2, default=str))

            # -----------------------------
            # LOG TOOL ERROR
            # -----------------------------
            if event["event"] == "on_tool_error":
                tool = event["name"]
                error = event["data"]["error"]
                print("\n❌ TOOL ERROR")
                print(f"Tool: {tool}")
                print(f"Error: {error}\n")

            # -----------------------------
            # STREAM MODEL TOKENS
            # -----------------------------
            if event["event"] == "on_chat_model_stream":
                chunk = event["data"]["chunk"].content
                if chunk:
                    yield chunk

        yield "[END]"

    return StreamingResponse(stream(), media_type="text/plain")
