from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ProjectManagerBase(BaseModel):
    user_id: str = Field(..., description="User ID of the project manager")
    name: str = Field(..., description="Project manager name")
    email: str = Field(..., description="Project manager email")

class ProjectManagerCreate(ProjectManagerBase):
    pass

class ProjectManagerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None

class ProjectManager(ProjectManagerBase):
    id: str = Field(..., description="Project manager ID")
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ProjectManagerAssignment(BaseModel):
    project_manager_id: str
    organization_id: str
    role: str  # project_manager, senior_project_manager