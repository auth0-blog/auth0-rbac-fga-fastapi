from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class RoleType(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"
    PROJECT_MANAGER = "project_manager"
    SENIOR_PROJECT_MANAGER = "senior_project_manager"

class RoleBase(BaseModel):
    name: str = Field(..., description="Role name")
    description: Optional[str] = Field(None, description="Role description")
    permissions: List[str] = Field(default_factory=list, description="List of permissions")

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[str]] = None

class Role(RoleBase):
    id: str = Field(..., description="Role ID")
    
    class Config:
        from_attributes = True

class UserRole(BaseModel):
    user_id: str
    role: RoleType
    organization_id: Optional[str] = None
    resource_type: str = "organization"  # organization, project, etc.