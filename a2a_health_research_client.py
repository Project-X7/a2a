import asyncio
import logging
from typing import Any
from uuid import uuid4
from helpers import display_agent_card

import httpx
from a2a.client import A2ACardResolver, A2AClient, ClientFactory
from a2a.types import (
    AgentCard,
    MessageSendParams,
    SendMessageRequest,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8080"


async def main() -> None:
    async with httpx.AsyncClient() as httpx_client:

        # 1. Resolve agent card
        resolver = A2ACardResolver(httpx_client=httpx_client, base_url=BASE_URL)
        agent_card: AgentCard = await resolver.get_agent_card()
        display_agent_card(agent_card)
        logger.info("Connected to agent: %s", agent_card.name)

        # 2. Create client
        client = A2AClient(httpx_client=httpx_client, agent_card=agent_card)

        # 3. Build payload
        payload: dict[str, Any] = {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": "What can you do?"}],
                "messageId": uuid4().hex,
            }
        }

        # 4. Send message
        request = SendMessageRequest(
            id=str(uuid4()),
            params=MessageSendParams(**payload),
        )
        response = await client.send_message(request)
        print(response.model_dump(mode="json", exclude_none=True))


if __name__ == "__main__":
    asyncio.run(main())