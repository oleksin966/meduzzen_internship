from fastapi import APIRouter, Depends, HTTPException, status, Security, Body
from db.models import User
from db.database import get_async_session
from schemas.user_schema import TokenSchema, UserSchema, UserSignUp, UserEmail, UserEditNamePass
from utils.auth import VerifyToken, create_access_token, get_current_user
from utils.utils import verify_password, check_existing_user, get_user_by_field, get_auth_user, hash_password
from sqlalchemy.ext.asyncio import AsyncSession
from services.user_service import UserServiceCrud
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import Union

router_auth = APIRouter()
auth = VerifyToken()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@router_auth.post('/signup/', summary="Sign Up user", response_model=UserSchema)
async def signup(
        user: UserSignUp = Depends(UserSignUp), 
        session: AsyncSession = Depends(get_async_session)
    ):

    await check_existing_user(session, User.username, user.username)
    await check_existing_user(session, User.email, user.email) # check if email exist, catch error

    user_service = UserServiceCrud(session)
    return await user_service.create_user(user)

@router_auth.post('/login', summary="Create access tokens for user", response_model=TokenSchema)
async def login(
        session: AsyncSession = Depends(get_async_session), 
        form_data: OAuth2PasswordRequestForm = Depends()    
    ):
    user = await get_user_by_field(session, User.username, form_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    hashed_pass = user.password
    if not verify_password(form_data.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    
    return {
        "token": create_access_token(data = {"sub": user.username,"email": user.email}),
        "token_type": "bearer"
    }


@router_auth.get("/me", summary="Get current user", response_model=Union[UserSchema, UserEmail])
async def private(
        session: AsyncSession = Depends(get_async_session),
        email: UserEmail = Depends(get_current_user),
        token: str = Security(auth.verify)
    ): 
    user = await get_auth_user(session, email)
    return user

@router_auth.get("/token", summary="Get token info")
async def token(
        token: str = Security(auth.verify)
    ):
    return token # GET TOKEN 

@router_auth.put("/edit/me", summary="Edit my Profile", response_model=UserSchema)
async def edit_me(
        data: UserEditNamePass = Depends(),
        session: AsyncSession = Depends(get_async_session),
        email: UserEmail = Depends(get_current_user),
        token: str = Security(auth.verify),
    ):
    
    user = await get_auth_user(session, email)

    get_data = data.model_dump()
    if get_data["username"] is not None:
        user.username = get_data["username"]
    else:
        get_data.pop("username", None)

    if get_data["password"] is not None:
        get_data["password"] = hash_password(get_data["password"])
    else:
         get_data.pop("password", None)
        
    user_service = UserServiceCrud(session)
    updated_user = await user_service.update_user(user.id, get_data)
    return updated_user

@router_auth.delete("/delete/me", summary="Delete my Profile", response_model=UserSchema)
async def delete_me(
        session: AsyncSession = Depends(get_async_session),
        email: UserEmail = Depends(get_current_user),
        token: str = Security(auth.verify),
    ):
    
    user = await get_auth_user(session, email)
    user_service = UserServiceCrud(session)
    delete_user = await user_service.delete_user(user.id)
    return delete_user
