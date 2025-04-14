from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.agents.llm_agent import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai.types import Content, Part
import os
import logging
from datetime import datetime

APP_NAME = "parallel_story_builder"
USER_ID = "creative_user"
SESSION_ID = "story_session_01"
GEMINI_MODEL = "gemini-1.5-flash"

LOG_DIR = "adk_logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f"code_feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(), logging.FileHandler(LOG_FILE)]
)

logger = logging.getLogger(__name__)
# Step 1: Define the agents
# --- Define Creative Sub-Agents ---

# Character Agent
character_agent = LlmAgent(
    name="CharacterDesigner",
    model=GEMINI_MODEL,
    instruction="""
You are a master of character design.
Generate a compelling main character for a short story based on the user's theme.
Include name, age, personality traits, and motivations in 2-3 sentences.
""",
    description="Creates the main character.",
)

# Plot Agent
plot_agent = LlmAgent(
    name="PlotArchitect",
    model=GEMINI_MODEL,
    instruction="""
You are a creative storyteller.
Based on the user's theme, outline a 3-part plot structure (Beginning, Conflict, Resolution) in bullet points.
Keep it concise and engaging.
""",
    description="Designs the story plot.",
)

# Setting Agent
setting_agent = LlmAgent(
    name="SettingMaster",
    model=GEMINI_MODEL,
    instruction="""
You are a world-builder.
Describe a vivid setting for the story based on the user's theme.
Use sensory details and imagery in 2-3 sentences.
""",
    description="Builds the story world.",
)

# --- Parallel Agent to run them simultaneously ---
story_outline_agent = ParallelAgent(
    name="StoryOutlineCreator",
    sub_agents=[character_agent, plot_agent, setting_agent]
)

# --- Set up session and runner ---
session_service = InMemorySessionService()
session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
runner = Runner(agent=story_outline_agent, app_name=APP_NAME, session_service=session_service)

# --- Function to run it ---
def generate_story_outline(theme):
    print(f"Theme: {theme}")
    content = Content(role="user", parts=[Part(text=theme)])
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    for event in events:
        if event.is_final_response() and event.content and event.content.parts:
            print("\n📘 Final Story Outline:\n")
            print(event.content.parts[0].text)
    logger.info(f"Log output saved to: {LOG_FILE}")

# --- Trigger it ---
if __name__ == "__main__":
    generate_story_outline("A world where AI dominaes humanity.")
