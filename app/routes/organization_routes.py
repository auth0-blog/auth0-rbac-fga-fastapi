from fastapi import APIRouter, HTTPException, Query
from typing import List
import uuid
from datetime import datetime

from app.models.organization import (
    Organization, 
    OrganizationCreate, 
    OrganizationUpdate,
    MemberAssignment
)
from app.services.authorization_service import authz_service

router = APIRouter()

# In-memory storage for demo purposes
organizations_db = {}

@router.get("/", response_model=List[Organization])
async def list_organizations(
    user_id: str = Query(..., description="User ID for authorization")
):
    """List all organizations where the user has at least member access."""
    accessible_orgs = []
    for org_id, org in organizations_db.items():
        if await authz_service.can_view_member(user_id, org_id):
            accessible_orgs.append(org)
    return accessible_orgs

@router.get("/{organization_id}", response_model=Organization)
async def get_organization(
    organization_id: str,
    user_id: str = Query(..., description="User ID for authorization")
):
    """Get a specific organization."""
    if not await authz_service.can_view_member(user_id, organization_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if organization_id not in organizations_db:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    return organizations_db[organization_id]

@router.post("/", response_model=Organization)
async def create_organization(
    organization: OrganizationCreate,
    user_id: str = Query(..., description="User ID for authorization")
):
    """Create a new organization. Creator becomes admin."""
    org_id = str(uuid.uuid4())
    new_org = Organization(
        id=org_id,
        name=organization.name,
        description=organization.description,
        created_at=datetime.now()
    )
    
    organizations_db[org_id] = new_org
    
    # Assign creator as admin
    await authz_service.assign_user_to_organization(user_id, org_id, "admin")
    
    return new_org

@router.put("/{organization_id}", response_model=Organization)
async def update_organization(
    organization_id: str,
    organization: OrganizationUpdate,
    user_id: str = Query(..., description="User ID for authorization")
):
    """Update an organization (admin only)."""
    if not await authz_service.can_add_member(user_id, organization_id):
        raise HTTPException(status_code=403, detail="Admin access required")
    
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
    """Delete an organization (admin only)."""
    if not await authz_service.can_add_member(user_id, organization_id):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if organization_id not in organizations_db:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    del organizations_db[organization_id]
    return {"message": "Organization deleted successfully"}

@router.post("/{organization_id}/members")
async def add_member(
    organization_id: str,
    member: MemberAssignment,
    user_id: str = Query(..., description="User ID for authorization")
):
    """Add a member to an organization (admin only)."""
    if not await authz_service.can_add_member(user_id, organization_id):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if organization_id not in organizations_db:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    if member.role not in ["admin", "member"]:
        raise HTTPException(status_code=400, detail="Role must be 'admin' or 'member'")
    
    success = await authz_service.assign_user_to_organization(
        member.user_id, 
        organization_id, 
        member.role
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to assign role")
    
    return {"message": f"User {member.user_id} added as {member.role}"}

@router.delete("/{organization_id}/members/{member_user_id}")
async def remove_member(
    organization_id: str,
    member_user_id: str,
    role: str = Query(..., description="Role to remove ('admin' or 'member')"),
    user_id: str = Query(..., description="User ID for authorization")
):
    """Remove a member from an organization (admin only)."""
    if not await authz_service.can_delete_member(user_id, organization_id):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if organization_id not in organizations_db:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    if role not in ["admin", "member"]:
        raise HTTPException(status_code=400, detail="Role must be 'admin' or 'member'")
    
    success = await authz_service.remove_user_from_organization(
        member_user_id, 
        organization_id, 
        role
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to remove role")
    
    return {"message": f"User {member_user_id} removed from {role} role"}