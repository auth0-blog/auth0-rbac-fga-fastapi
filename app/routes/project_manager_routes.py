from fastapi import APIRouter, HTTPException, Query
from typing import List
import uuid
from datetime import datetime

from app.models.project_manager import (
    ProjectManager, 
    ProjectManagerCreate, 
    ProjectManagerUpdate,
    ProjectManagerAssignment
)
from app.services.authorization_service import auth_service

router = APIRouter()

# In-memory storage for demo purposes
project_managers_db = {}

@router.get("/", response_model=List[ProjectManager])
async def list_project_managers(
    user_id: str = Query(..., description="User ID for authorization"),
    organization_id: str = Query(None, description="Filter by organization")
):
    """List all project managers."""
    # For simplicity, allowing read access if user has any role in the org
    if organization_id:
        has_access = await auth_service.check_read_access(user_id, organization_id)
        if not has_access:
            raise HTTPException(status_code=403, detail="No access to this organization")
    
    return list(project_managers_db.values())

@router.get("/{pm_id}", response_model=ProjectManager)
async def get_project_manager(
    pm_id: str,
    user_id: str = Query(..., description="User ID for authorization")
):
    """Get a specific project manager."""
    if pm_id not in project_managers_db:
        raise HTTPException(status_code=404, detail="Project manager not found")
    
    return project_managers_db[pm_id]

@router.post("/", response_model=ProjectManager)
async def create_project_manager(
    pm: ProjectManagerCreate,
    user_id: str = Query(..., description="User ID for authorization")
):
    """Create a new project manager profile."""
    pm_id = str(uuid.uuid4())
    new_pm = ProjectManager(
        id=pm_id,
        user_id=pm.user_id,
        name=pm.name,
        email=pm.email,
        created_at=datetime.now()
    )
    
    project_managers_db[pm_id] = new_pm
    return new_pm

@router.put("/{pm_id}", response_model=ProjectManager)
async def update_project_manager(
    pm_id: str,
    pm_update: ProjectManagerUpdate,
    user_id: str = Query(..., description="User ID for authorization")
):
    """Update a project manager profile."""
    if pm_id not in project_managers_db:
        raise HTTPException(status_code=404, detail="Project manager not found")
    
    existing_pm = project_managers_db[pm_id]
    
    # Only allow the PM themselves or org admins to update
    if existing_pm.user_id != user_id:
        raise HTTPException(status_code=403, detail="Can only update your own profile")
    
    update_data = pm_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(existing_pm, field, value)
    
    return existing_pm

@router.post("/{pm_id}/assign")
async def assign_project_manager(
    pm_id: str,
    assignment: ProjectManagerAssignment,
    user_id: str = Query(..., description="User ID for authorization")
):
    """Assign a project manager to an organization."""
    # Check if user has admin access to the organization
    has_admin = await auth_service.check_admin_access(user_id, assignment.organization_id)
    if not has_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if pm_id not in project_managers_db:
        raise HTTPException(status_code=404, detail="Project manager not found")
    
    pm = project_managers_db[pm_id]
    is_senior = assignment.role == "senior_project_manager"
    
    success = await auth_service.assign_project_manager(
        pm.user_id, 
        assignment.organization_id, 
        is_senior
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to assign project manager")
    
    return {"message": f"Project manager assigned as {assignment.role}"}

@router.delete("/{pm_id}/assign/{organization_id}")
async def remove_project_manager_assignment(
    pm_id: str,
    organization_id: str,
    role: str = Query(..., description="Role to remove (project_manager or senior_project_manager)"),
    user_id: str = Query(..., description="User ID for authorization")
):
    """Remove a project manager assignment from an organization."""
    # Check if user has admin access to the organization
    has_admin = await auth_service.check_admin_access(user_id, organization_id)
    if not has_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if pm_id not in project_managers_db:
        raise HTTPException(status_code=404, detail="Project manager not found")
    
    pm = project_managers_db[pm_id]
    is_senior = role == "senior_project_manager"
    
    success = await auth_service.remove_project_manager(
        pm.user_id, 
        organization_id, 
        is_senior
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to remove project manager")
    
    return {"message": f"Project manager removed from {role} role"}