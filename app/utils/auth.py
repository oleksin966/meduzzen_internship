from typing import Optional
from core.config import settings
from datetime import datetime, timedelta
from jwt import encode, InvalidTokenError
from fastapi.security import SecurityScopes, HTTPAuthorizationCredentials, HTTPBearer
from fastapi import  HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from db.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User
from schemas.user_schema import TokenPayload
from pydantic import ValidationError
from utils.utils import decode_token
from utils.exceptions import UnauthenticatedException, UnauthorizedException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class VerifyToken:    
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

    #check if email exist: 
    email = payload.get("email")

    if email is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )
    
    return email

def create_access_token(data: dict):
    expires_time = datetime.utcnow() + timedelta(hours=1)
    to_encode = data.copy()
    to_encode.update({"exp": expires_time})
    return encode(to_encode, settings.SIGNING_KEY, algorithm=settings.AUTH0_ALGORITHMS)




