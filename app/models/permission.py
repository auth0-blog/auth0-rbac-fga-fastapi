from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class PermissionType(str, Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    MANAGE_MEMBERS = "manage_members"
    MANAGE_PROJECTS = "manage_projects"

class PermissionBase(BaseModel):
    name: str = Field(..., description="Permission name")
    description: Optional[str] = Field(None, description="Permission description")
    resource_type: str = Field(..., description="Type of resource this permission applies to")

class PermissionCreate(PermissionBase):
    pass

class PermissionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    resource_type: Optional[str] = None

class Permission(PermissionBase):
    id: str = Field(..., description="Permission ID")
    
    class Config:
        from_attributes = True

class PermissionCheck(BaseModel):
    user_id: str
    permission: PermissionType
    resource_id: str
    resource_type: str = "organization"