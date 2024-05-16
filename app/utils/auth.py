from typing import Optional
from core.config import settings
from datetime import datetime, timedelta, timezone
from jwt import encode, InvalidTokenError
from fastapi.security import SecurityScopes, HTTPAuthorizationCredentials, HTTPBearer
from fastapi import  HTTPException, Depends, status, Security
from db.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User
from schemas.user_schema import TokenPayload
from pydantic import ValidationError
from utils.utils import decode_token, get_auth_user
from utils.exceptions import UnauthenticatedException, UnauthorizedException

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
            decode_token(token.credentials)
        except Exception as error:
            raise UnauthorizedException(str(error))
    
        return token.credentials

auth = VerifyToken()

async def get_verified_token(token: str = Security(auth.verify)) -> str:
    return token

async def get_token_payload(token: str = Security(auth.verify)) -> dict:
    return decode_token(token)

async def get_current_user(
        session: AsyncSession = Depends(get_async_session), 
        token: str = Depends(get_verified_token)
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
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email = payload.get("email")

    if email is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )
    
    return await get_auth_user(session, email)

def create_access_token(data: dict):
    expires_time = datetime.utcnow() + timedelta(hours=6)
    to_encode = data.copy()
    to_encode.update({"exp": expires_time})
    return encode(to_encode, settings.SIGNING_KEY, algorithm=settings.AUTH0_ALGORITHMS)




