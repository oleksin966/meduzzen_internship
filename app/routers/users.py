from schemas.user_schema import UserSchema,UserSignUp,UserUpdate,UserDetail
from utils.utils import hash_password, Paginate
from typing import List
from fastapi import APIRouter, Depends, HTTPException

from db.sqlquery import UsersSqlQuery
from db.models import User
from db.database import get_async_session

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.logging import logger

router_user = APIRouter() 
crud = UsersSqlQuery(User)

### ROUTES FROM DATABASE ###
@router_user.get("/users_list/", response_model=List[UserSchema])
async def get_all_users(db: AsyncSession = Depends(get_async_session), offset: int = 0, limit: int = 5):
    paginator = Paginate(db, User, offset, limit)
    users = await paginator.fetch_results()
    return users


@router_user.get("/user_detail/{user_id}", response_model=UserDetail)
async def get_user_by_id(user_id: int):
    user = await crud.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user":user}


@router_user.post("/create/")
async def create_user(data: UserSignUp = Depends()):
    try:
        get_model = data.model_dump()
        hashed_password = await hash_password(get_model["password"]) #hash pass
        get_model["password"] = hashed_password
        result = await crud.create(get_model)

        if not result:
            raise HTTPException(status_code=500, detail="Failed to create user")
        logger.info("User created successfully: %s", result)
        return result
    except Exception as e:
        logger.error("Error occurred while creating user: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router_user.put("/update/")
async def update_user(user_id: int, data: UserUpdate):
    try:
        get_model = data.model_dump()
        result = await crud.update(user_id, get_model)

        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        logger.info("User updated successfully: %s", result)
        return result
    except Exception as e:
        logger.error("Error occurred while updating user: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router_user.delete("/delete/")
async def delete_user(user_id: int):
    try:
        result = await crud.delete(user_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        logger.info("User deleted successfully: %s", result)
        return result
    except Exception as e:
        logger.error("Error occurred while deleting user: %s", e)
        raise HTTPException(status_code=500, detail=str(e))



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