import os
from dotenv import load_dotenv
from google.adk.agents import SequentialAgent # orchetrator for agents
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent # create a2a compatible client
from google.adk.runners import InMemoryRunner ## for running the agent in-memory (no server needed)
from helpers import mute_logs, display_markdown
import asyncio

load_dotenv()
mute_logs()

host = os.environ.get("AGENT_HOST")
policy_port = os.environ.get("POLICY_AGENT_PORT")
research_port = os.environ.get("RESEARCH_AGENT_PORT")


## Create A2A client for each agent
policy_agent = RemoteA2aAgent(name="InsurancePolicyCoverageAgent", agent_card = f"http://{host}:{policy_port}")
research_agent = RemoteA2aAgent(name="HealthResearchAgent", agent_card = f"http://{host}:{research_port}")

## Create a root agent to orchestrate the conversation
orchestrator = SequentialAgent(
    name="Orchestrator",
    description="An agent that orchestrates a conversation between a policy agent and a health research agent. The user will ask a health insurance question, and the orchestrator will first ask the policy agent to interpret the question and identify relevant policy details. Then, it will ask the research agent to provide healthcare information based on the user's question and the policy details provided by the policy agent. Finally, the orchestrator will combine the information from both agents to provide a comprehensive answer to the user.",
    sub_agents=
    [
        research_agent,
          policy_agent,
    ],
)

print("Running Orchestrator Agent...")
prompt = "How can I get mental health therapy?"

print("Running Healthcare Workflow Agent")

runner = InMemoryRunner(orchestrator)

async def run_agent(prompt: str):
    for event in await runner.run_debug(prompt, quiet=True):
        if event.is_final_response() and event.content:
            display_markdown(event.content.parts[0].text)
asyncio.run(run_agent(prompt))