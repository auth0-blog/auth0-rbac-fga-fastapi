from typing import List, Optional
from openfga_sdk.client.models import ClientTuple
from app.utils.openfga_client import openfga_client

class AuthorizationService:
    """Simple RBAC authorization service using OpenFGA."""
    
    async def assign_user_to_organization(self, user_id: str, organization_id: str, role: str) -> bool:
        """Assign a user to an organization with a specific role (admin or member)."""
        if role not in ["admin", "member"]:
            raise ValueError("Role must be 'admin' or 'member'")
            
        client_tuple = ClientTuple(
            user=f"user:{user_id}",
            relation=role,
            object=f"organization:{organization_id}"
        )
        return await openfga_client.write_tuples([client_tuple])
    
    async def remove_user_from_organization(self, user_id: str, organization_id: str, role: str) -> bool:
        """Remove a user's role from an organization."""
        if role not in ["admin", "member"]:
            raise ValueError("Role must be 'admin' or 'member'")
            
        client_tuple = ClientTuple(
            user=f"user:{user_id}",
            relation=role,
            object=f"organization:{organization_id}"
        )
        return await openfga_client.delete_tuples([client_tuple])
    
    async def assign_resource_to_organization(self, resource_id: str, organization_id: str) -> bool:
        """Assign a resource to an organization."""
        client_tuple = ClientTuple(
            user=f"organization:{organization_id}",
            relation="organization",
            object=f"resource:{resource_id}"
        )
        return await openfga_client.write_tuples([client_tuple])
    
    async def can_add_member(self, user_id: str, organization_id: str) -> bool:
        """Check if user can add members to organization (admin only)."""
        return await openfga_client.check_permission(
            user=f"user:{user_id}",
            relation="can_add_member",
            object_id=f"organization:{organization_id}"
        )
    
    async def can_delete_member(self, user_id: str, organization_id: str) -> bool:
        """Check if user can delete members from organization (admin only)."""
        return await openfga_client.check_permission(
            user=f"user:{user_id}",
            relation="can_delete_member",
            object_id=f"organization:{organization_id}"
        )
    
    async def can_view_member(self, user_id: str, organization_id: str) -> bool:
        """Check if user can view members of organization (admin or member)."""
        return await openfga_client.check_permission(
            user=f"user:{user_id}",
            relation="can_view_member",
            object_id=f"organization:{organization_id}"
        )
    
    async def can_add_resource(self, user_id: str, organization_id: str) -> bool:
        """Check if user can add resources to organization (admin or member)."""
        return await openfga_client.check_permission(
            user=f"user:{user_id}",
            relation="can_add_resource",
            object_id=f"organization:{organization_id}"
        )
    
    async def can_delete_resource(self, user_id: str, resource_id: str) -> bool:
        """Check if user can delete a resource (admin only)."""
        return await openfga_client.check_permission(
            user=f"user:{user_id}",
            relation="can_delete_resource",
            object_id=f"resource:{resource_id}"
        )
    
    async def can_view_resource(self, user_id: str, resource_id: str) -> bool:
        """Check if user can view a resource (admin or member)."""
        return await openfga_client.check_permission(
            user=f"user:{user_id}",
            relation="can_view_resource",
            object_id=f"resource:{resource_id}"
        )

# Global authorization service instance
authz_service = AuthorizationService()