from fastapi import APIRouter, HTTPException, Query
from typing import List
import uuid

from app.models.permission import (
    Permission, 
    PermissionCreate, 
    PermissionUpdate, 
    PermissionCheck,
    PermissionType
)
from app.services.authorization_service import auth_service

router = APIRouter()

# In-memory storage for demo purposes
permissions_db = {}

@router.get("/", response_model=List[Permission])
async def list_permissions(
    user_id: str = Query(..., description="User ID for authorization")
):
    """List all available permissions."""
    return list(permissions_db.values())

@router.get("/{permission_id}", response_model=Permission)
async def get_permission(
    permission_id: str,
    user_id: str = Query(..., description="User ID for authorization")
):
    """Get a specific permission."""
    if permission_id not in permissions_db:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    return permissions_db[permission_id]

@router.post("/", response_model=Permission)
async def create_permission(
    permission: PermissionCreate,
    user_id: str = Query(..., description="User ID for authorization")
):
    """Create a new permission (system admin only)."""
    # In a real system, you'd check if user is a system admin
    permission_id = str(uuid.uuid4())
    new_permission = Permission(
        id=permission_id,
        name=permission.name,
        description=permission.description,
        resource_type=permission.resource_type
    )
    
    permissions_db[permission_id] = new_permission
    return new_permission

@router.put("/{permission_id}", response_model=Permission)
async def update_permission(
    permission_id: str,
    permission_update: PermissionUpdate,
    user_id: str = Query(..., description="User ID for authorization")
):
    """Update a permission (system admin only)."""
    if permission_id not in permissions_db:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    existing_permission = permissions_db[permission_id]
    update_data = permission_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(existing_permission, field, value)
    
    return existing_permission

@router.post("/check")
async def check_permission(
    permission_check: PermissionCheck,
    requesting_user_id: str = Query(..., description="User ID making the request")
):
    """Check if a user has a specific permission on a resource."""
    # Allow users to check their own permissions or admins to check others
    if permission_check.user_id != requesting_user_id:
        # Check if requesting user is admin of the resource
        if permission_check.resource_type == "organization":
            has_admin = await auth_service.check_admin_access(
                requesting_user_id, 
                permission_check.resource_id
            )
            if not has_admin:
                raise HTTPException(
                    status_code=403, 
                    detail="Can only check your own permissions or admin access required"
                )
    
    has_permission = await auth_service.check_permission(
        permission_check.user_id,
        permission_check.permission,
        permission_check.resource_id,
        permission_check.resource_type
    )
    
    return {
        "user_id": permission_check.user_id,
        "permission": permission_check.permission,
        "resource_id": permission_check.resource_id,
        "resource_type": permission_check.resource_type,
        "allowed": has_permission
    }

@router.get("/user/{user_id}/permissions")
async def get_user_permissions(
    user_id: str,
    organization_id: str = Query(..., description="Organization to check permissions for"),
    requesting_user_id: str = Query(..., description="User ID making the request")
):
    """Get all permissions a user has for a specific organization."""
    # Allow users to check their own permissions or admins to check others
    if user_id != requesting_user_id:
        has_admin = await auth_service.check_admin_access(requesting_user_id, organization_id)
        if not has_admin:
            raise HTTPException(
                status_code=403, 
                detail="Can only check your own permissions or admin access required"
            )
    
    # Check each permission type
    permissions = {}
    for perm_type in PermissionType:
        has_perm = await auth_service.check_permission(
            user_id, perm_type, organization_id, "organization"
        )
        permissions[perm_type.value] = has_perm
    
    return {
        "user_id": user_id,
        "organization_id": organization_id,
        "permissions": permissions
    }