from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
import uuid
from datetime import datetime

from app.models.organization import (
    Organization, 
    OrganizationCreate, 
    OrganizationUpdate, 
    OrganizationMember
)
from app.models.role import RoleType
from app.services.authorization_service import auth_service

router = APIRouter()

# In-memory storage for demo purposes
organizations_db = {}

async def check_organization_access(user_id: str, organization_id: str, required_permission: str = "read"):
    """Dependency to check if user has access to organization."""
    if required_permission == "admin":
        has_access = await auth_service.check_admin_access(user_id, organization_id)
    elif required_permission == "write":
        has_access = await auth_service.check_write_access(user_id, organization_id)
    else:
        has_access = await auth_service.check_read_access(user_id, organization_id)
    
    if not has_access:
        raise HTTPException(
            status_code=403, 
            detail=f"Insufficient permissions for {required_permission} access to organization"
        )

@router.get("/", response_model=List[Organization])
async def list_organizations(
    user_id: str = Query(..., description="User ID for authorization")
):
    """List all organizations the user has access to."""
    accessible_orgs = []
    for org_id, org in organizations_db.items():
        if await auth_service.check_read_access(user_id, org_id):
            accessible_orgs.append(org)
    return accessible_orgs

@router.get("/{organization_id}", response_model=Organization)
async def get_organization(
    organization_id: str,
    user_id: str = Query(..., description="User ID for authorization")
):
    """Get a specific organization."""
    await check_organization_access(user_id, organization_id, "read")
    
    if organization_id not in organizations_db:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    return organizations_db[organization_id]

@router.post("/", response_model=Organization)
async def create_organization(
    organization: OrganizationCreate,
    user_id: str = Query(..., description="User ID for authorization")
):
    """Create a new organization."""
    org_id = str(uuid.uuid4())
    new_org = Organization(
        id=org_id,
        name=organization.name,
        description=organization.description,
        created_at=datetime.now()
    )
    
    organizations_db[org_id] = new_org
    
    # Assign creator as admin
    await auth_service.assign_role_to_user(user_id, RoleType.ADMIN, org_id)
    
    return new_org

@router.put("/{organization_id}", response_model=Organization)
async def update_organization(
    organization_id: str,
    organization: OrganizationUpdate,
    user_id: str = Query(..., description="User ID for authorization")
):
    """Update an organization."""
    await check_organization_access(user_id, organization_id, "write")
    
    if organization_id not in organizations_db:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    existing_org = organizations_db[organization_id]
    update_data = organization.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(existing_org, field, value)
    
    return existing_org

@router.delete("/{organization_id}")
async def delete_organization(
    organization_id: str,
    user_id: str = Query(..., description="User ID for authorization")
):
    """Delete an organization."""
    await check_organization_access(user_id, organization_id, "admin")
    
    if organization_id not in organizations_db:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    del organizations_db[organization_id]
    return {"message": "Organization deleted successfully"}

@router.post("/{organization_id}/members")
async def add_member(
    organization_id: str,
    member: OrganizationMember,
    user_id: str = Query(..., description="User ID for authorization")
):
    """Add a member to an organization."""
    await check_organization_access(user_id, organization_id, "admin")
    
    if organization_id not in organizations_db:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    role = RoleType(member.role)
    success = await auth_service.assign_role_to_user(member.user_id, role, organization_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to assign role")
    
    return {"message": f"User {member.user_id} added as {member.role}"}

@router.delete("/{organization_id}/members/{member_user_id}")
async def remove_member(
    organization_id: str,
    member_user_id: str,
    role: str = Query(..., description="Role to remove"),
    user_id: str = Query(..., description="User ID for authorization")
):
    """Remove a member from an organization."""
    await check_organization_access(user_id, organization_id, "admin")
    
    if organization_id not in organizations_db:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    role_type = RoleType(role)
    success = await auth_service.remove_role_from_user(member_user_id, role_type, organization_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to remove role")
    
    return {"message": f"User {member_user_id} removed from {role}"}