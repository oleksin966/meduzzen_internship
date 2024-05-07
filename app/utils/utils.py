from passlib.context import CryptContext
from sqlalchemy import select, Column
from core.config import settings
from db.models import User, Company
from core.config import settings
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from jwt import decode, encode, InvalidTokenError
from pydantic import ValidationError
from schemas.user_schema import UserEmail


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
    def __init__(self, db: AsyncSession, model: type, page: int, options=None, where=None):
        self.db = db
        self.model = model
        self.filterr = filterr
        self.page = page
        self.options = options
        self.where = where
        self.COUNT = 3

    async def fetch_results(self):
        if self.page is None or self.page < 1:
            self.page = 1
        
        offset = (self.page - 1) * self.COUNT
        limit = self.COUNT

        statement = select(self.model)

        if self.options is not None:
            statement = statement.options(*self.options)
        if self.where is not None:
            statement = statement.where(self.where)

        
        statement = statement.offset(offset).limit(limit)
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

async def get_auth_user(session, email):
    user_in_db = await get_user_by_field(session, User.email, email)
    if user_in_db:
        return user_in_db
    else:
        return UserEmail(email=email)
