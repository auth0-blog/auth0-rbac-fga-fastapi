from openfga_sdk import OpenFgaClient
from openfga_sdk.client import ClientConfiguration
from openfga_sdk.client.models import ClientCheckRequest, ClientWriteRequest, ClientTuple
from openfga_sdk.credentials import Credentials, CredentialConfiguration
from app.config import settings
import logging

# Set up logging
logger = logging.getLogger(__name__)

class Auth0FGAClient:
    def __init__(self):
        # Get Auth0 FGA configuration from settings
        if not all([settings.auth0_fga_store_id, settings.auth0_fga_client_id, 
                    settings.auth0_fga_client_secret]):
            raise ValueError("Missing required Auth0 FGA configuration: " \
            "AUTH0_FGA_STORE_ID, AUTH0_FGA_CLIENT_ID, AUTH0_FGA_CLIENT_SECRET")

        # Initialize OpenFgaClient with configuration
        configuration = ClientConfiguration(
            api_url=settings.auth0_fga_api_url,
            store_id=settings.auth0_fga_store_id,
            authorization_model_id=settings.auth0_fga_authorization_model_id,
            credentials= Credentials(
                method="client_credentials",
                configuration= CredentialConfiguration(
                    client_id= settings.auth0_fga_client_id,
                    client_secret= settings.auth0_fga_client_secret,
                    api_audience= settings.auth0_fga_api_audience,
                    api_issuer= settings.auth0_fga_api_token_issuer
                )
            )
        )
        
        self.client = OpenFgaClient(configuration)

    async def check_permission(self, user: str, relation: str, object_id: str) -> bool:
        """Check if a user has a specific relation to an object."""
        try:
            response = await self.client.check(ClientCheckRequest(
                user=user,
                relation=relation,
                object=object_id
            ))
            logger.debug(f"Permission check result: {response.allowed}")
            return response.allowed
        except Exception as e:
            logger.error(f"Error checking permission for user={user}, relation={relation}, object={object_id}: {e}")
            return False

    async def write_tuples(self, tuples: list[ClientTuple]) -> bool:
        """Write relationship tuples to Auth0 FGA."""
        try:
            logger.debug(f"Writing {len(tuples)} tuples to Auth0 FGA")
            write_request = ClientWriteRequest(
                writes=tuples
            )
            
            await self.client.write(write_request)
            logger.debug("Tuples written successfully")
            return True
        except Exception as e:
            logger.error(f"Error writing tuples: {e}")
            return False

    async def delete_tuples(self, tuples: list[ClientTuple]) -> bool:
        """Delete relationship tuples from Auth0 FGA."""
        try:
            logger.debug(f"Deleting {len(tuples)} tuples from Auth0 FGA")
            write_request = ClientWriteRequest(
                deletes=tuples
            )
            await self.client.write(write_request)
            logger.debug("Tuples deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Error deleting tuples: {e}")
            return False
    
    async def list_objects(self, user: str, relation: str, object_type: str) -> list[str]:
        """List all objects of a given type that a user has a specific relation to."""
        try:
            logger.debug(f"Listing objects: user={user}, relation={relation}, type={object_type}")
            response = await self.client.list_objects(
                user=user,
                relation=relation,
                type=object_type
            )
            objects = response.objects if hasattr(response, 'objects') else []
            logger.debug(f"Found {len(objects)} objects")
            return objects
        except Exception as e:
            logger.error(f"Error listing objects for user={user}, relation={relation}, type={object_type}: {e}")
            return []
    
    async def health_check(self) -> bool:
        """Check if the Auth0 FGA service is healthy."""
        try:
            # Simple health check by attempting to read authorization models
            await self.client.read_authorization_models()
            return True
        except Exception as e:
            logger.error(f"Auth0 FGA health check failed: {e}")
            return False

# Global client instance
openfga_client = Auth0FGAClient()