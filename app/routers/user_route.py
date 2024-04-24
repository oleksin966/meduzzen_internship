from schemas.user_schema import UserSchema,UserSignUp,UserUpdate,UserDetail,UserList
from typing import List
from fastapi import APIRouter, Depends, HTTPException

from db.models import User
from db.database import get_async_session

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from services.user_service import UserServiceCrud

router_user = APIRouter()


@router_user.get('/users/list/', response_model=List[UserSchema])
async def users_list(
        page: int,
        session: AsyncSession = Depends(get_async_session)
    ):
    user_service = UserServiceCrud(session)
    return await user_service.get_all_users(page)

@router_user.get('/users/{user_id}', response_model=UserSchema)
async def get_user(
        user_id: int, 
        session: AsyncSession = Depends(get_async_session)
    ):
    user_service = UserServiceCrud(session)
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router_user.post('/create/', response_model=UserSchema)
async def create_user_route(
        user: UserSignUp = Depends(UserSchema), 
        session: AsyncSession = Depends(get_async_session)
    ):
    user_service = UserServiceCrud(session)
    return await user_service.create_user(user)

@router_user.put('/update/', response_model=UserUpdate)
async def update_user_route(
        user_id: int, 
        data: UserUpdate, 
        session: AsyncSession = Depends(get_async_session)
    ):
    get_data = data.model_dump()
    user_service = UserServiceCrud(session)
    user = await user_service.update_user(user_id, get_data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router_user.delete('/delete/', response_model=UserSchema)
async def delete_user_route(
        user_id: int, 
        session: AsyncSession = Depends(get_async_session)
    ):
    user_service = UserServiceCrud(session)
    user = await user_service.delete_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

### TESTING USERS SCHEMAS ###

#from utils.test_data import users

# @router_user.get("/users/", response_model=List[UserUpdate])
# async def get_user_models():
#     return users

# @router_user.get("/users/list/", response_model=UserList)
# async def get_users_list():
#     return {"users": users }

# @router_user.get("/users/detail/{user_id}", response_model=UserDetail)
# async def get_user_detail(user_id: int):
#     for user in users:
#         if user["id"] == user_id:
#             return {"user": user}
#     return None
    #return {"user":next((user for user in users if user["id"] == user_id), None)}