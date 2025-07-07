from fastapi import APIRouter, HTTPException, Query
from typing import List
import uuid

from app.models.role import Role, RoleCreate, RoleUpdate, UserRole, RoleType
from app.services.authorization_service import auth_service

router = APIRouter()

# In-memory storage for demo purposes
roles_db = {}

@router.get("/", response_model=List[Role])
async def list_roles(
    user_id: str = Query(..., description="User ID for authorization")
):
    """List all available roles."""
    return list(roles_db.values())

@router.get("/{role_id}", response_model=Role)
async def get_role(
    role_id: str,
    user_id: str = Query(..., description="User ID for authorization")
):
    """Get a specific role."""
    if role_id not in roles_db:
        raise HTTPException(status_code=404, detail="Role not found")
    
    return roles_db[role_id]

@router.post("/", response_model=Role)
async def create_role(
    role: RoleCreate,
    user_id: str = Query(..., description="User ID for authorization")
):
    """Create a new role (system admin only)."""
    # In a real system, you'd check if user is a system admin
    role_id = str(uuid.uuid4())
    new_role = Role(
        id=role_id,
        name=role.name,
        description=role.description,
        permissions=role.permissions
    )
    
    roles_db[role_id] = new_role
    return new_role

@router.put("/{role_id}", response_model=Role)
async def update_role(
    role_id: str,
    role_update: RoleUpdate,
    user_id: str = Query(..., description="User ID for authorization")
):
    """Update a role (system admin only)."""
    if role_id not in roles_db:
        raise HTTPException(status_code=404, detail="Role not found")
    
    existing_role = roles_db[role_id]
    update_data = role_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(existing_role, field, value)
    
    return existing_role

@router.post("/assign")
async def assign_user_role(
    user_role: UserRole,
    admin_user_id: str = Query(..., description="Admin user ID for authorization")
):
    """Assign a role to a user for a specific organization."""
    if user_role.organization_id:
        # Check if admin has admin access to the organization
        has_admin = await auth_service.check_admin_access(admin_user_id, user_role.organization_id)
        if not has_admin:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        success = await auth_service.assign_role_to_user(
            user_role.user_id, 
            user_role.role, 
            user_role.organization_id
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to assign role")
        
        return {"message": f"Role {user_role.role} assigned to user {user_role.user_id}"}
    
    raise HTTPException(status_code=400, detail="Organization ID is required")

@router.delete("/assign")
async def remove_user_role(
    user_role: UserRole,
    admin_user_id: str = Query(..., description="Admin user ID for authorization")
):
    """Remove a role from a user for a specific organization."""
    if user_role.organization_id:
        # Check if admin has admin access to the organization
        has_admin = await auth_service.check_admin_access(admin_user_id, user_role.organization_id)
        if not has_admin:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        success = await auth_service.remove_role_from_user(
            user_role.user_id, 
            user_role.role, 
            user_role.organization_id
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to remove role")
        
        return {"message": f"Role {user_role.role} removed from user {user_role.user_id}"}
    
    raise HTTPException(status_code=400, detail="Organization ID is required")