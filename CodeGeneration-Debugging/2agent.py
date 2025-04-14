
import os
import logging
from datetime import datetime
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
# from google.genai import configure
from google.genai.types import Content, Part

# Configure Gemini
# configure(api_key=os.getenv("GOOGLE_API_KEY"))  # Set your API key in environment

# Constants
APP_NAME = "autogen_clone"
USER_ID = "user"
SESSION_ID = "session1"
MODEL = "gemini-1.5-flash"  # Or 1.5-flash

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

planner = LlmAgent(
    name="Planner",
    model=MODEL,
    instruction="""
You are a Planner AI. Given a user query, break the problem into a sequence of subtasks.
Respond in bullet points, one for each step.
""",
    # output_key="subtasks"
)

coder = LlmAgent(
    name="Coder",
    model=MODEL,
    instruction="""
You are a Python programmer. Take the list of subtasks and write clean Python code to accomplish all of them.
Wrap your code in a Python code block.
""",
    # input_keys=["subtasks"],
    # output_key="code"
)

critic = LlmAgent(
    name="Critic",
    model=MODEL,
    instruction="""
You are a code reviewer. Review the Python code provided and provide suggestions for improvement.
Focus on correctness, efficiency, and clarity.
""",
    # input_keys=["code"],
    # output_key="review"
)

# Step 2: Compose the pipeline using SequentialAgent

pipeline = SequentialAgent(
    name="AutoGenPipeline",
    sub_agents=[planner, coder, critic]
)

# Step 3: Setup session and runner

session_service = InMemorySessionService()
session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
runner = Runner(agent=pipeline, app_name=APP_NAME, session_service=session_service)

# Step 4: Run the system

def run_autogen_clone(user_query):
    print(f"User Query: {user_query}")
    content = Content(role="user", parts=[Part(text=user_query)])
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    final_output = None
    for event in events:
        if event.is_final_response() and event.content and event.content.parts:
            final_output = event.content.parts[0].text

    if final_output:
        print("\nFinal Output from Critic:\n", final_output)
    else:
        print("\nNo final response received.")

    logger.info(f"Log output saved to: {LOG_FILE}")

# Example usage
# --- Trigger Execution ---
if __name__ == "__main__":
    run_autogen_clone("Write a function to scrape titles from a Wikipedia page and save them to a CSV.")