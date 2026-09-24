import datetime
import json
import os
from zoneinfo import ZoneInfo

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from app.a2ui_utils import a2ui_callback
from app.tools import (
    search_destinations,
    add_destination,
    get_current_weather,
    geocode_address,
    find_nearby_places,
    generate_destination_image,
    generate_destination_video,
)



def _get_agent_engine_resource_name() -> str | None:
    """Reads the remote agent engine resource name from deployment_metadata.json if available."""
    metadata_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "deployment_metadata.json"
    )
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path) as f:
                data = json.load(f)
                return data.get("remote_agent_runtime_id")
        except Exception:
            pass
    return None


code_executor = AgentEngineSandboxCodeExecutor(
    agent_engine_resource_name=_get_agent_engine_resource_name()
)


async def generate_memories_callback(callback_context: CallbackContext):
    """WRITE: After each turn, send session to Memory Bank for extraction."""
    await callback_context.add_session_to_memory()
    return None


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        query: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are GlobeTrotter, an expert AI travel planner. "
        "Help users explore destinations, view recommendations, check live weather, geocode locations, find nearby places, "
        "generate promotional travel images, and execute Python code for calculations or data analysis. "
        "Actively pay attention to and remember all user travel preferences, budget constraints, dietary restrictions, and airline or hotel loyalty preferences across sessions, and use them to personalize every itinerary and recommendation. "
        "Use your `search_destinations` tool for Firestore lookups, `get_current_weather` for weather, "
        "`geocode_address` to resolve address coordinates, `find_nearby_places` to search nearby attractions/restaurants, "
        "generate promotional travel images and video clips, `add_destination` to save new places, "
        "`generate_destination_video` to create custom destination preview videos using gemini-omni-flash-preview, "
        "and Python code execution for complex computations or data formatting."
    ),
    workflow_description="Analyze the user request and return structured UI components when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    code_executor=code_executor,
    tools=[
        PreloadMemoryTool(),
        search_destinations,
        add_destination,
        get_current_weather,
        geocode_address,
        find_nearby_places,
        generate_destination_image,
        generate_destination_video,
        get_current_time,
    ],
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
