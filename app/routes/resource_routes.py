from fastapi import APIRouter, HTTPException, Query
from typing import List
import uuid
from datetime import datetime

from app.models.resource import (
    Resource, 
    ResourceCreate, 
    ResourceUpdate
)
from app.services.authorization_service import authz_service

router = APIRouter()

# In-memory storage for demo purposes
resources_db = {}

@router.get("/", response_model=List[Resource])
async def list_resources(
    user_id: str = Query(..., description="User ID for authorization"),
    organization_id: str = Query(None, description="Filter by organization")
):
    """List all resources the user can view."""
    accessible_resources = []
    for resource_id, resource in resources_db.items():
        # If organization filter is provided, check if user has access to that org
        if organization_id and resource.organization_id != organization_id:
            continue
        
        if await authz_service.can_view_resource(user_id, resource_id):
            accessible_resources.append(resource)
    
    return accessible_resources

@router.get("/{resource_id}", response_model=Resource)
async def get_resource(
    resource_id: str,
    user_id: str = Query(..., description="User ID for authorization")
):
    """Get a specific resource."""
    if not await authz_service.can_view_resource(user_id, resource_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if resource_id not in resources_db:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    return resources_db[resource_id]

@router.post("/", response_model=Resource)
async def create_resource(
    resource: ResourceCreate,
    user_id: str = Query(..., description="User ID for authorization")
):
    """Create a new resource (admin or member of organization)."""
    if not await authz_service.can_add_resource(user_id, resource.organization_id):
        raise HTTPException(status_code=403, detail="Cannot add resources to this organization")
    
    resource_id = str(uuid.uuid4())
    new_resource = Resource(
        id=resource_id,
        name=resource.name,
        description=resource.description,
        resource_type=resource.resource_type,
        organization_id=resource.organization_id,
        created_at=datetime.now()
    )
    
    resources_db[resource_id] = new_resource
    
    # Link resource to organization in OpenFGA
    await authz_service.assign_resource_to_organization(resource_id, resource.organization_id)
    
    return new_resource

@router.put("/{resource_id}", response_model=Resource)
async def update_resource(
    resource_id: str,
    resource_update: ResourceUpdate,
    user_id: str = Query(..., description="User ID for authorization")
):
    """Update a resource (admin only)."""
    if not await authz_service.can_delete_resource(user_id, resource_id):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if resource_id not in resources_db:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    existing_resource = resources_db[resource_id]
    update_data = resource_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(existing_resource, field, value)
    
    return existing_resource

@router.delete("/{resource_id}")
async def delete_resource(
    resource_id: str,
    user_id: str = Query(..., description="User ID for authorization")
):
    """Delete a resource (admin only)."""
    if not await authz_service.can_delete_resource(user_id, resource_id):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if resource_id not in resources_db:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    del resources_db[resource_id]
    return {"message": "Resource deleted successfully"}

@router.get("/{resource_id}/permissions")
async def check_resource_permissions(
    resource_id: str,
    user_id: str = Query(..., description="User ID to check permissions for")
):
    """Check what permissions a user has on a specific resource."""
    if resource_id not in resources_db:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    permissions = {
        "can_view": await authz_service.can_view_resource(user_id, resource_id),
        "can_delete": await authz_service.can_delete_resource(user_id, resource_id)
    }
    
    return {
        "resource_id": resource_id,
        "user_id": user_id,
        "permissions": permissions
    }