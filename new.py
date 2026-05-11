import os
import httpx
from helpers import display_agent_card
from a2a.client import (
    Client,
    ClientConfig,
    ClientFactory,
    create_text_message_object,
)
from a2a.types import AgentCard, Artifact, Message, Task
from a2a.utils.message import get_message_text
from dotenv import load_dotenv
_ = load_dotenv()

host = os.environ.get("AGENT_HOST", "localhost")
port = os.environ.get("POLICY_AGENT_PORT")
# port = os.environ.get("RESEARCH_AGENT_PORT") 

prompt = "How much would I pay for mental health therapy?"
# prompt = "How do I get mental health therapy?"

from rich.console import Console
from rich.markdown import Markdown

console = Console()

async def main():
    async with httpx.AsyncClient(timeout=100.0) as httpx_client: # type: ignore
        # Step 1: Create a client
        client: Client = await ClientFactory.connect(     #type: ignore
            f"http://{host}:{port}",
            client_config=ClientConfig(
                httpx_client=httpx_client,
            ),
        )

        # Step 2: Discover the agent by fetching its card
        agent_card = await client.get_card()   #type: ignore
        display_agent_card(agent_card)

        # Step 3: Create the message using a convenient helper function
        message = create_text_message_object(content=prompt)

        console.print(Markdown(f"**Sending prompt:** `{prompt}` to the agent..."))

        # Step 4: Send the message and await the final response.
        responses = client.send_message(message)

        text_content = ""

        # Step 5: Process the responses from the agent
        async for response in responses: # type: ignore
            if isinstance(response, Message):
                # The agent replied directly with a final message
                print(f"Message ID: {response.message_id}")
                text_content = get_message_text(response)
            # response is a ClientEvent
            elif isinstance(response, tuple):
                task: Task = response[0]
                print(f"Task ID: {task.id}")
                if task.artifacts:
                    artifact: Artifact = task.artifacts[0]
                    print(f"Artifact ID: {artifact.artifact_id}")
                    text_content = get_message_text(artifact)

        console.print(Markdown("### Final Agent Response\n-----"))
        if text_content:
            console.print(Markdown(text_content))
        else:
            console.print(
                Markdown(
                    """**No final text content received or task did not 
                    complete successfully.**"""
                )
            )
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())