from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from core.config import settings
from typing import AsyncGenerator
from fastapi import Depends

DATABASE_URL = settings.database_url

async_engine = create_async_engine(DATABASE_URL, echo=True)

async_session = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session




