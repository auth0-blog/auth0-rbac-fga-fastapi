import asyncio
from typing import Optional, Dict, Any
from openfga_sdk import OpenFgaClient
from openfga_sdk.client import ClientConfiguration
from openfga_sdk.client.models import ClientCheckRequest, ClientWriteRequest, ClientTuple
from dotenv import load_dotenv
import os

class OpenFGAClient:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()

        configuration = ClientConfiguration(
            api_url=os.getenv("OPENFGA_API_URL"),
            store_id=os.getenv("OPENFGA_STORE_ID"),
            authorization_model_id=os.getenv("OPENFGA_AUTHORIZATION_MODEL_ID"),
        )
        print(f"Connecting to OpenFGA at {os.getenv("OPENFGA_API_URL")} with store ID {os.getenv("OPENFGA_STORE_ID")}")
        self.client = OpenFgaClient(configuration)

    async def check_permission(self, user: str, relation: str, object_id: str) -> bool:
        """Check if a user has a specific relation to an object."""
        try:
            response = await self.client.check(ClientCheckRequest(
                user=user,
                relation=relation,
                object=object_id
            ))
            return response.allowed
        except Exception as e:
            print(f"Error checking permission: {e}")
            return False

    async def write_tuples(self, tuples: list[ClientTuple]) -> bool:
        """Write relationship tuples to OpenFGA."""
        try:
            write_request = ClientWriteRequest(
                writes=tuples
            )
            
            await self.client.write(write_request)
            return True
        except Exception as e:
            print(f"Error writing tuples: {e}")
            return False

    async def delete_tuples(self, tuples: list[ClientTuple]) -> bool:
        """Delete relationship tuples from OpenFGA."""
        try:
            write_request = ClientWriteRequest(
                deletes=tuples
            )
            await self.client.write(write_request)
            return True
        except Exception as e:
            print(f"Error deleting tuples: {e}")
            return False

# Global client instance
openfga_client = OpenFGAClient()