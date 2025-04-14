import os
import logging
from datetime import datetime
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# --- Configuration ---
GEMINI_MODEL = "gemini-1.5-flash"
APP_NAME = "code_execution_with_feedback"
USER_ID = "local_user"
SESSION_ID = "local_session"

LOG_DIR = "adk_logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f"code_feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(), logging.FileHandler(LOG_FILE)]
)

logger = logging.getLogger(__name__)

# --- Define Agents ---

user_proxy = LlmAgent(
    name="User_Proxy",
    model=GEMINI_MODEL,
    instruction="You are a helpful assistant. Interact with the Programmer to solve a task.",
    output_key="user_prompt"
)

programmer = LlmAgent(
    name="Programmer",
    model=GEMINI_MODEL,
    instruction="You are a skilled programmer. Write and execute Python code to solve tasks. "
                "Seek clarification from the User_Proxy if needed. Output only the code.",
    output_key="code_result"
)

critic = LlmAgent(
    name="Critic",
    model=GEMINI_MODEL,
    instruction="You are a code critic. Review the result in 'code_result'. "
                "Provide feedback to the Programmer. Focus on correctness and improvements.",
    output_key="review_feedback"
)

# --- Create the Sequential Agent Workflow ---
workflow = SequentialAgent(
    name="CodeExecutionPipeline",
    sub_agents=[user_proxy, programmer, critic]
)

# --- Set up Session and Runner ---
session_service = InMemorySessionService()
session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
runner = Runner(agent=workflow, app_name=APP_NAME, session_service=session_service)

# --- Run the Workflow ---
def call_agent(task_description):
    logger.info(f"Task Description: {task_description}")
    content = types.Content(role="user", parts=[types.Part(text=task_description)])
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    # Process final response
    for event in events:
        if event.is_final_response():
            logger.info("\n--- Final Response ---")
            print(event.content.parts[0].text)

    logger.info(f"Log output saved to: {LOG_FILE}")


# --- Trigger Execution ---
if __name__ == "__main__":
    call_agent("Write Python code to calculate the create a tic tac toe game.")
