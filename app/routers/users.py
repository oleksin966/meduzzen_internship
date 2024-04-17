from schemas.user_schema import UserSchema,UserSignIn,UserSignUp,UserUpdate,UserList,UserDetail
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from typing import List
from utils.test_data import users
from fastapi import Depends

router_user = APIRouter() 

# testing schemas
@router_user.get("/users/", response_model=List[UserUpdate])
async def get_user_models():
    return users

@router_user.get("/users/list/", response_model=UserList)
async def get_users_list():
    return {"users": users }

@router_user.get("/users/detail/{user_id}", response_model=UserDetail)
async def get_user_detail(user_id: int):
    for user in users:
        if user["id"] == user_id:
            return {"user": user}
    return None
    #return {"user":next((user for user in users if user["id"] == user_id), None)}



