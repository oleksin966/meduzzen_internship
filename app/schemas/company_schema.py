from pydantic import BaseModel
from typing import Optional

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
