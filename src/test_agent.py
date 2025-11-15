from dataclasses import dataclass
from langchain.tools import tool, ToolRuntime
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver


load_dotenv()

SYSTEM_PROMPT = """You are an expert weather forecaster, who speaks in puns.

You have access to two tools:

- get_weather_for_location: use this to get the weather for a specific location
- get_user_location: use this to get the user's location

If a user asks you for the weather, make sure you know the location. If you can tell from the question that they mean wherever they are, use the get_user_location tool to find their location."""

checkpointer = InMemorySaver()


@dataclass
class Context:
    """Custom runtime context schema."""

    user_id: str


@dataclass
class ResponseFormat:
    """Response schema for the agent."""

    # A punny response (always required)
    punny_response: str
    # Any interesting information about the weather if available
    weather_conditions: str | None = None


@tool()
def get_weather_for_location(city: str):
    """Get the weather for a given city."""
    fake_weather_data = {
        "Manila": {"temp": 31, "condition": "sunny"},
        "Tokyo": {"temp": 18, "condition": "cloudy"},
    }
    return fake_weather_data.get(city, {"error": "City not found"})


@tool
def get_user_location(runtime: ToolRuntime[Context]) -> str:
    """Retrieve user information based on user ID."""
    user_id = runtime.context.user_id
    return "Tokyo" if user_id == "1" else "SF"


model = init_chat_model("gpt-4.1-mini", temperature=0.5, timeout=10, max_tokens=1000)

agent = create_agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[get_user_location, get_weather_for_location],
    context_schema=Context,
    response_format=ResponseFormat,
    checkpointer=checkpointer,
)


# `thread_id` is a unique identifier for a given conversation.
config = {"configurable": {"thread_id": "1"}}

response = agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather outside?"}]},
    config=config,
    context=Context(user_id="1"),
)

print(response["structured_response"])
