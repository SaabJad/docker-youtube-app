from google.adk.agents import LlmAgent, Agent 
# from google.adk.tools import google_search, built_in_code_execution 
from google.adk.tools import agent_tool 
from google.adk.tools import google_search
from google.adk.code_executors import BuiltInCodeExecutor
import os

def load_instruction_from_file(
    filename: str, default_instruction: str = "Default instruction."
) -> str:
    """Reads instruction text from a file relative to this script."""
    instruction = default_instruction
    try:
        # Construct path relative to the current script file (__file__)
        filepath = os.path.join(os.path.dirname(__file__), filename)
        with open(filepath, "r", encoding="utf-8") as f:
            instruction = f.read()
        print(f"Successfully loaded instruction from {filename}")
    except FileNotFoundError:
        print(f"WARNING: Instruction file not found: {filepath}. Using default.")
    except Exception as e:
        print(f"ERROR loading instruction file {filepath}: {e}. Using default.")
    return instruction

# ----------------------------------------------------------------------------------

Agent_Search = LlmAgent(
    model='gemini-2.0-flash-exp',
    name='SearchAgent',
    description="An agent that can search the web.",
    instruction="""
    You're a spealist in Google Search
    """,
    # tools=[google_search]
    tools=[google_search],
)
Agent_Code = LlmAgent(
    model='gemini-2.0-flash-exp',
    name='CodeAgent',
    description="An agent that can execute code.",
    instruction="""
    You're a specialist in Code Execution
    """,
    # tools=[built_in_code_execution]
    code_executor=BuiltInCodeExecutor()
)

# Sub Agent 1: Scriptwriter
scriptwriter_agent = LlmAgent(
    name="ShortsScriptwriter",
    model="gemini-2.0-flash-001",
    instruction=load_instruction_from_file("scriptwriter_instruction.txt"),
    tools=[agent_tool.AgentTool(agent=Agent_Search), 
        #    agent_tool.AgentTool(agent=Agent_Code)
           ],
    # sub_agents=[Agent_Search, Agent_Code],
    output_key="generated_script",  # Save result to state

    # disallow_transfer_to_parent=True,  
    # disallow_transfer_to_peers=False

)

# Sub Agent 2: Visualizer
visualizer_agent = LlmAgent(
    name="ShortsVisualizer",
    model="gemini-2.0-flash-001",
    instruction=load_instruction_from_file("visualizer_instruction.txt"),
    description="Generates visual concepts based on a provided script.",
    output_key="visual_concepts",  # Save result to state
)

# Sub Agent 3: Formatter
# This agent would read both state keys and combine into the final Markdown
formatter_agent = LlmAgent(
    name="ConceptFormatter",
    model="gemini-2.0-flash-001",
    instruction="""Combine the script from state['generated_script'] and the visual concepts from state['visual_concepts'] into the final Markdown format requested previously (Hook, Script & Visuals table, Visual Notes, CTA).""",
    description="Formats the final Short concept.",
    output_key="final_short_concept",
)


# Llm Agent Workflow
youtube_shorts_agent = LlmAgent(
    name="youtube_shorts_agent",
    model="gemini-2.0-flash-001",
    instruction=load_instruction_from_file("shorts_agent_instruction.txt"),
    description="An agent that can write scripts, visuals and format youtube short videos.",
    # tools=[agent_tool.AgentTool(agent=scriptwriter_agent), 
    #        agent_tool.AgentTool(agent=visualizer_agent), 
    #        agent_tool.AgentTool(agent=formatter_agent)],
    sub_agents=[scriptwriter_agent, visualizer_agent, formatter_agent],
)

root_agent = youtube_shorts_agent


# Code required to make the agent programmatically runnable.
from google.genai import types 
from google.adk.sessions import InMemorySessionService 
from google.adk.runners import Runner 

# Load .env
# Replace the API_KEY in .env file.
from dotenv import load_dotenv 

load_dotenv()

# Instantiate constants
APP_NAME = "youtube_shorts_app"
USER_ID = "12345"
SESSION_ID = "123344"

# Session and Runner
session_service = InMemorySessionService()
session = session_service.create_session(
    app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
)
runner = Runner(
    agent=youtube_shorts_agent, app_name=APP_NAME, session_service=session_service
)

if __name__ == "__main__":

    while True:
        query = input("Enter query (or type 'exit' to quit): ")
        if query.lower() == "exit":
            break

        content = types.Content(role="user", parts=[types.Part(text=query)])
        events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

        for event in events:
            if event.is_final_response():
                final_response = event.content.parts[0].text
                print("Agent Response: ", final_response)