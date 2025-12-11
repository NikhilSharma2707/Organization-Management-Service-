from pydantic import BaseModel, EmailStr

class OrgCreate(BaseModel):
    organization_name: str
    email: EmailStr
    password: str

class OrgGet(BaseModel):
    organization_name: str

class OrgUpdate(BaseModel):
    old_organization_name: str
    new_organization_name: str
    email: EmailStr
    password: str

class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class OrgOut(BaseModel):
    _id: str | None
    organization_name: str
    collection_name: str
    admin_email: EmailStr
