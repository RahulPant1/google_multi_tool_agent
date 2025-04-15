import dotenv
import textwrap
from google.adk.runners import InMemoryRunner
from google.genai.types import Part, UserContent
from agent import root_agent  # Assuming this is where your SequentialAgent is defined


def run_agent_audit(user_input: str):
    dotenv.load_dotenv()

    runner = InMemoryRunner(agent=root_agent)
    session = runner.session_service.create_session(
        app_name=runner.app_name, user_id="local_user"
    )

    content = UserContent(parts=[Part(text=user_input)])

    print("\nLLM Auditor: Verifying and refining...\n")
    events = list(runner.run(
        user_id=session.user_id,
        session_id=session.id,
        new_message=content
    ))

    for event in events:
        if event.content and event.content.parts:
            print(event.content.parts[0].text)


if __name__ == '__main__':
    input_text = textwrap.dedent("""\
        Question: Are LLMs always right?
        Answer: Yes, they are never wrong.
    """).strip()
    run_agent_audit(input_text)
