# run_debate.py

from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from agent import root_agent
from dotenv import load_dotenv
import os
import json
from datetime import datetime
import re

load_dotenv()

# App Constants
APP_NAME = "debate_app"
USER_ID = "user_001"
SESSION_ID = "session_001"

# Create output directory if it doesn't exist
OUTPUT_DIR = "debate_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Session and Runner Setup
session_service = InMemorySessionService()
session = session_service.create_session(
    app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
)
runner = Runner(
    agent=root_agent, app_name=APP_NAME, session_service=session_service
)

# Helper function to identify content type
def identify_content_type(text):
    # Check if this is the winner announcement
    if text.startswith("Winner:") or "Winner:" in text:
        return "winner"
    
    # Check if this is a counter-argument (Con side)
    if text.startswith("Counter-Argument") or "Counter-Argument" in text:
        return "con_argument"
    
    # Otherwise, assume it's a pro argument
    return "pro_argument"

# Agent Interaction
def start_debate(topic: str):
    print("\n🔥 Starting Debate on:", topic)
    content = types.Content(role="user", parts=[types.Part(text=topic)])
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    # Prepare data structure to store all debate content
    debate_data = {
        "topic": topic,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "pro_arguments": [],
        "con_arguments": [],
        "winner": ""
    }
    
    # Process all events
    for event in events:
        # Process only events with content
        if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts') and event.content.parts:
            response_text = event.content.parts[0].text
            content_type = identify_content_type(response_text)
            
            if content_type == "pro_argument":
                debate_data["pro_arguments"].append(response_text)
                print("\n🗣️ Pro Argument:\n")
                print(response_text)
            elif content_type == "con_argument":
                debate_data["con_arguments"].append(response_text)
                print("\n🗣️ Con Argument:\n")
                print(response_text)
            elif content_type == "winner":
                debate_data["winner"] = response_text
                print("\n🏆 Debate Result:\n")
                print(response_text)
    
    # Save debate data to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    sanitized_topic = "".join(c if c.isalnum() else "_" for c in topic)[:30]  # Sanitize topic for filename
    filename = f"{OUTPUT_DIR}/debate_{sanitized_topic}_{timestamp}.json"
    
    with open(filename, "w") as f:
        json.dump(debate_data, f, indent=2)
    
    print(f"\n💾 Debate saved to: {filename}")
    print(f"Pro arguments: {len(debate_data['pro_arguments'])}")
    print(f"Con arguments: {len(debate_data['con_arguments'])}")
    
    return debate_data

if __name__ == "__main__":
    topic = input("Enter the debate topic: ")
    start_debate(topic)
