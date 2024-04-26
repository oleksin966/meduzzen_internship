from passlib.context import CryptContext
from sqlalchemy import select, Column
from core.config import settings
from db.models import User 
from jwt import decode
from core.config import settings
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from jwt import decode, encode, InvalidTokenError
from pydantic import ValidationError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed_pass: str) -> bool:
    return pwd_context.verify(password, hashed_pass)

def decode_token(token: str):
    try:
        payload = decode(
            token,
            settings.SIGNING_KEY,
            algorithms=settings.AUTH0_ALGORITHMS,
            audience=settings.AUTH0_API_AUDIENCE,
            issuer=settings.AUTH0_ISSUER,
        )

        return payload
    except (InvalidTokenError, ValidationError):
        payload_without_auth0 = decode(
            token,
            settings.SIGNING_KEY,
            algorithms=settings.AUTH0_ALGORITHMS,
        )

        return payload_without_auth0
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not decode token",
            headers={"WWW-Authenticate": "Bearer"},
        )

class Paginate:
    def __init__(self, db: None, model: None, page: int | None = None):
        self.db = db
        self.model = model
        self.page = page
        self.COUNT = 3

    async def fetch_results(self):
        if self.page is None or self.page < 1:
            self.page = 1
        
        offset = (self.page - 1) * self.COUNT
        limit = self.COUNT

        statement = select(self.model).offset(offset).limit(limit)
        result = await self.db.execute(statement)
        return result.scalars().all()

async def check_existing_user(session, field, value):
    existing_user = await session.execute(select(User).where(field == value))
    if existing_user.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"{field} already exists")

async def get_user_by_field(session: AsyncSession, field: Column, value: str) -> User:
    query = select(User).where(field == value)
    user = await session.execute(query)
    return user.scalar_one_or_none()

