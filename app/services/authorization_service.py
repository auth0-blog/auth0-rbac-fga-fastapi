from typing import List, Optional
from openfga_sdk.models import TupleKey
from app.utils.openfga_client import openfga_client
from app.models.role import RoleType
from app.models.permission import PermissionType

class AuthorizationService:
    """Service for handling authorization operations with OpenFGA."""
    
    async def assign_role_to_user(self, user_id: str, role: RoleType, organization_id: str) -> bool:
        """Assign a role to a user for an organization."""
        tuple_key = TupleKey(
            user=f"user:{user_id}",
            relation=role.value,
            object=f"organization:{organization_id}"
        )
        return await openfga_client.write_tuples([tuple_key])
    
    async def remove_role_from_user(self, user_id: str, role: RoleType, organization_id: str) -> bool:
        """Remove a role from a user for an organization."""
        tuple_key = TupleKey(
            user=f"user:{user_id}",
            relation=role.value,
            object=f"organization:{organization_id}"
        )
        return await openfga_client.delete_tuples([tuple_key])
    
    async def check_permission(self, user_id: str, permission: PermissionType, resource_id: str, resource_type: str = "organization") -> bool:
        """Check if a user has a specific permission on a resource."""
        return await openfga_client.check_permission(
            user=f"user:{user_id}",
            relation=permission.value,
            object_id=f"{resource_type}:{resource_id}"
        )
    
    async def assign_project_manager(self, user_id: str, organization_id: str, is_senior: bool = False) -> bool:
        """Assign project manager role to a user."""
        role = RoleType.SENIOR_PROJECT_MANAGER if is_senior else RoleType.PROJECT_MANAGER
        return await self.assign_role_to_user(user_id, role, organization_id)
    
    async def remove_project_manager(self, user_id: str, organization_id: str, is_senior: bool = False) -> bool:
        """Remove project manager role from a user."""
        role = RoleType.SENIOR_PROJECT_MANAGER if is_senior else RoleType.PROJECT_MANAGER
        return await self.remove_role_from_user(user_id, role, organization_id)
    
    async def check_admin_access(self, user_id: str, organization_id: str) -> bool:
        """Check if user has admin access to an organization."""
        return await self.check_permission(user_id, PermissionType.ADMIN, organization_id)
    
    async def check_read_access(self, user_id: str, organization_id: str) -> bool:
        """Check if user has read access to an organization."""
        return await self.check_permission(user_id, PermissionType.READ, organization_id)
    
    async def check_write_access(self, user_id: str, organization_id: str) -> bool:
        """Check if user has write access to an organization."""
        return await self.check_permission(user_id, PermissionType.WRITE, organization_id)

# Global authorization service instance
auth_service = AuthorizationService()