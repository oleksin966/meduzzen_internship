from fastapi import APIRouter, Depends, HTTPException, status, Security
from db.models import User
from db.database import get_async_session
from schemas.user_schema import TokenSchema, UserSchema, UserSignUp, UserSignIn
from utils.auth import VerifyToken, create_access_token, get_current_user
from utils.utils import verify_password, check_existing_user, get_user_by_field
from sqlalchemy.ext.asyncio import AsyncSession
from services.user_service import UserServiceCrud
from fastapi.security import OAuth2PasswordRequestForm

router_auth = APIRouter()
auth = VerifyToken()


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
        "token": create_access_token(user.username, user.email),
    }


@router_auth.get("/me", summary="Get current user", response_model=UserSchema)
def private(
        user: UserSchema = Depends(get_current_user),
        token: str = Security(auth.verify) # make private endpoint
    ):
    return user #return logged user

@router_auth.get("/token", summary="Get token info")
def token(
        user: UserSchema = Depends(get_current_user),
        token: str = Security(auth.verify) # make private endpoint
    ):
    return {"token payload": token} #return payload from current token