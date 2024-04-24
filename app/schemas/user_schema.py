from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    pass

class UserSchema(UserBase):
    id: int
    username: str
    email: str
    password: str
    age: Optional[int] = None
    description: Optional[str] = None

class UserId(UserBase):
    id: int

class UserSignIn(UserBase):
    username: str
    password: str

class UserSignUp(UserBase):
    username: str
    password: str
    email: str
    age: Optional[int] = None
    description: Optional[str] = None

class UserSignUpEmail(UserBase):
    email: str

class UserUpdate(UserBase):
    age: Optional[int]
    description: Optional[str]
    password: Optional[str]
    username: Optional[str]

class UserList(UserBase):
    users: List[UserSchema]

class UserDetail(UserBase):
    user: UserSchema

class TokenSchema(BaseModel):
    token: str

class TokenPayload(BaseModel):
    sub: str
    exp: datetime  

    class Config:
        populate_by_name = True

