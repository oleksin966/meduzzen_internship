from pydantic import BaseModel

class UserBase(BaseModel):
    pass

class User(UserBase):
    id: int
    username: str
    age: int
    email: str
    password: str
    description: str

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
    users: list[User]

class UserDetail(UserBase):
    user: User
