from typing import Optional
from core.config import settings
from datetime import datetime, timedelta, timezone
from jwt import PyJWKClient, encode, InvalidTokenError
from fastapi.security import SecurityScopes, HTTPAuthorizationCredentials, HTTPBearer
from fastapi import  HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from db.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User
from schemas.user_schema import UserSchema, TokenPayload
from pydantic import ValidationError
from utils.utils import get_user_by_field, decode_token
from utils.exceptions import UnauthenticatedException, UnauthorizedException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class VerifyToken:
    def __init__(self):
        self.config = settings
        jwks_url = f'https://{self.config.AUTH0_DOMAIN}/.well-known/jwks.json'
        self.jwks_client = PyJWKClient(jwks_url)
    
    async def verify(
            self,
            security_scopes: SecurityScopes,
            token: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer())
        ):
        if token is None:
            raise UnauthenticatedException()
        try:
            payload = decode_token(token.credentials)
        except Exception as error:
            raise UnauthorizedException(str(error))
    
        return payload


async def get_current_user(
        session: AsyncSession = Depends(get_async_session), 
        token: str = Depends(oauth2_scheme)
    ) -> User:
    try:
        payload = decode_token(token)
        token_data = TokenPayload(**payload)
        if token_data.exp < datetime.now(timezone.utc):
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    #check if username from payload token exist in DB:    
    user = await get_user_by_field(session, User.username, token_data.sub) 

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )
    
    return user

def create_access_token(
        username: str, 
        email: Optional[str] = None, 
        expires_time: Optional[int] = None
    ) -> str:
    if expires_time is not None:
        expires_time = datetime.utcnow() + timedelta(minutes=expires_time)
    else:
        expires_time = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload = {
        "exp": expires_time, 
        "iss": str(settings.AUTH0_ISSUER), 
        "aud": str(settings.AUTH0_API_AUDIENCE),
        "sub": str(username), #add username to payload
        "email": str(email) #add email to payload
    }
    encoded_jwt = encode(
        payload,
        key=settings.SIGNING_KEY,
        algorithm=settings.AUTH0_ALGORITHMS,
    )
    return encoded_jwt

