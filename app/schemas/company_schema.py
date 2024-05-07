from pydantic import BaseModel, Field
from typing import Optional, List
from schemas.user_schema import UserUsername, UserSchema

class CompanyBase(BaseModel):
    pass

class CompanyCreate(CompanyBase):
    name: str
    description: str

class CompanyUpdate(CompanyBase):
    name: Optional[str] = None
    description: Optional[str] = None
    visibility: Optional[bool] = None

class CompanySchema(CompanyBase):
    id: int
    name: str
    description: str
    owner_id: int
    visibility: bool

class CompanyName(CompanyBase):
    id: int
    name: str

class CompanyActionSchema(BaseModel):
    user: UserUsername 
    company: CompanyName

class InvitationSent(CompanyActionSchema):
    message: str = "Invitation sent succesfully."

class InvitationCancel(CompanyActionSchema):
    message: str = "Invitation canceled succesfully."

class InvitationAccept(CompanyActionSchema):
    message: str = "Invitation accepted succesfully."

class InvitationReject(CompanyActionSchema):
    message: str = "Invitation rejected succesfully"


class RequestSent(CompanyActionSchema):
    message: str = "Request sent succesfully."

class RequestCancel(CompanyActionSchema):
    message: str = "Request canceled succesfully."

class RequestAccept(CompanyActionSchema):
    message: str = "Request accepted succesfully."

class Requestreject(CompanyActionSchema):
    message: str = "Request rejected succesfully."


class DeleteFromCompany(CompanyActionSchema):
    message: str = "User deleted from company succesfully."

class LeaveCompany(CompanyActionSchema):
    message: str = "You leaved company succesfully."

class CompanyUsers(BaseModel):
    user: UserSchema