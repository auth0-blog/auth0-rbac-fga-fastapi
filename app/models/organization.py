from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class OrganizationBase(BaseModel):
    name: str = Field(..., description="Organization name")
    description: Optional[str] = Field(None, description="Organization description")

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class Organization(OrganizationBase):
    id: str = Field(..., description="Organization ID")
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class OrganizationMember(BaseModel):
    user_id: str
    organization_id: str
    role: str  # admin, member, viewer