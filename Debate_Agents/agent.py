# agent.py

from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
import os
from dotenv import load_dotenv

from datetime import datetime
import re

load_dotenv()

def load_instruction(filename: str) -> str:
    path = os.path.join("instructions", filename)
    with open(path, "r") as file:
        return file.read()

# --- Pro side agent ---
pro_agent = LlmAgent(
    name="ProAgent",
    model="gemini-2.0-flash",
    instruction=load_instruction("pro_instruction.txt"),
    output_key="pro_argument",
)

# --- Con side agent ---
con_agent = LlmAgent(
    name="ConAgent",
    model="gemini-2.0-flash",
    instruction=load_instruction("con_instruction.txt"),
    output_key="con_argument",
)

# --- Parallel Agent ---
parallel_debate_agent = ParallelAgent(
    name="ParallelDebateAgent",
    sub_agents=[pro_agent, con_agent],
)

# --- Judge Agent ---
judge_agent = LlmAgent(
    name="JudgeAgent",
    model="gemini-2.0-flash",
    instruction=load_instruction("judge_instruction.txt"),
    output_key="debate_judgement",
)

# --- Debate Workflow Agent ---
debate_workflow_agent = SequentialAgent(
    name="DebateWorkflowAgent",
    sub_agents=[parallel_debate_agent, judge_agent],
)

root_agent = debate_workflow_agent