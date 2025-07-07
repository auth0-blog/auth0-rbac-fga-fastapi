import asyncio
from typing import Optional, Dict, Any
from openfga_sdk import OpenFgaClient
from openfga_sdk.client import ClientConfiguration
from openfga_sdk.models import CheckRequest, TupleKey, WriteRequest, WriteRequestWrites
from app.config import settings

class OpenFGAClient:
    def __init__(self):
        configuration = ClientConfiguration(
            api_url=settings.openfga_api_url,
            store_id=settings.openfga_store_id,
            authorization_model_id=settings.openfga_authorization_model_id,
        )
        self.client = OpenFgaClient(configuration)

    async def check_permission(self, user: str, relation: str, object_id: str) -> bool:
        """Check if a user has a specific relation to an object."""
        try:
            response = await self.client.check(CheckRequest(
                tuple_key=TupleKey(
                    user=user,
                    relation=relation,
                    object=object_id
                )
            ))
            return response.allowed
        except Exception as e:
            print(f"Error checking permission: {e}")
            return False

    async def write_tuples(self, tuples: list[TupleKey]) -> bool:
        """Write relationship tuples to OpenFGA."""
        try:
            write_request = WriteRequest(
                writes=WriteRequestWrites(tuple_keys=tuples)
            )
            await self.client.write(write_request)
            return True
        except Exception as e:
            print(f"Error writing tuples: {e}")
            return False

    async def delete_tuples(self, tuples: list[TupleKey]) -> bool:
        """Delete relationship tuples from OpenFGA."""
        try:
            write_request = WriteRequest(
                deletes=WriteRequestWrites(tuple_keys=tuples)
            )
            await self.client.write(write_request)
            return True
        except Exception as e:
            print(f"Error deleting tuples: {e}")
            return False

# Global client instance
openfga_client = OpenFGAClient()