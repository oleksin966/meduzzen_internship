from schemas.user_schema import UserSchema,UserSignUp,UserUpdate,UserDetail,UserList,UserEditNamePass
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path

from db.models import User
from db.database import get_async_session

from sqlalchemy.ext.asyncio import AsyncSession
from services.user_service import UserServiceCrud

from utils.auth import get_current_user
router_user = APIRouter(prefix="/user")

@router_user.get('/all', summary="Get all Users", response_model=List[UserSchema])
async def users_list(
        page: int,
        session: AsyncSession = Depends(get_async_session)
    ):
    user_service = UserServiceCrud(session)
    return await user_service.get_all_users(page)

@router_user.get('/{user_id}', summary="Get User by ID", response_model=UserSchema)
async def get_user(
        user_id: int, 
        session: AsyncSession = Depends(get_async_session)
    ):
    user_service = UserServiceCrud(session)
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router_user.post('/create/', summary="Create", response_model=UserSchema)
async def create_user_route(
        user: UserSignUp = Depends(UserSchema), 
        session: AsyncSession = Depends(get_async_session)
    ):
    user_service = UserServiceCrud(session)
    return await user_service.create_user(user)

@router_user.put('/update/', summary="Update User", response_model=UserUpdate)
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

@router_user.put("/edit/{user_id}", summary="Edit my Profile", response_model=UserSchema)
async def edit_me(
        user_id: int = Path(..., title="The ID of the user to edit"),
        data: UserEditNamePass = Depends(),
        session: AsyncSession = Depends(get_async_session),
        user: UserSchema = Depends(get_current_user),
    ):

    if user.id != user_id:
        raise HTTPException(status_code=403, detail="You are not authorized to edit this user")

    get_data = data.dict(exclude_none=True)
    if "password" in get_data:
        get_data["password"] = hash_password(get_data["password"])
        
    user_service = UserServiceCrud(session)
    updated_user = await user_service.update_user(user.id, get_data)
    return updated_user

@router_user.delete("/delete/{user_id}", summary="Delete my Profile", response_model=UserSchema)
async def delete_me(
        user_id: int = Path(..., title="The ID of the user to delete"),
        session: AsyncSession = Depends(get_async_session),
        user: UserSchema = Depends(get_current_user),
    ):

    if user.id != user_id:
        raise HTTPException(status_code=403, detail="You are not authorized to delete this user")

    user_service = UserServiceCrud(session)
    delete_user = await user_service.delete_user(user.id)
    return delete_user

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