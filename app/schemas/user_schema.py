from pydantic import BaseModel
from typing import List, Optional

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

class UserUpdate(UserBase):
    age: int
    description: str
    password: str
    username: str

class UserList(UserBase):
    users: List[UserSchema]

class UserDetail(UserBase):
    user: UserSchema


