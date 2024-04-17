from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import OperationalError
from sqlalchemy import text, Table

from db.database import get_async_session
from db.redis import get_redis_client
from aioredis import Redis
from db.models import Base

from logging import getLogger

router_connects = APIRouter()

logger = getLogger(__name__)

#check database connection
@router_connects.get("/db/")
async def check_db_connection(session: AsyncSession = Depends(get_async_session)):
    try:
        await session.execute(text("SELECT 1"))
        return {
            'result': 'Working'
        }
    except OperationalError:
        raise HTTPException(status_code=500, detail="Could not connect to the Database")

#check redis connection
@router_connects.get("/redis/")
async def check_redis_connection(redis: Redis = Depends(get_redis_client)):
    try:
        pong = await redis.ping()
        return {"status": "Connected", "response": pong}
    except Exception as e:
        return {"status": "Error", "message": str(e)}

# check if table users exist
@router_connects.get("/db_users/")
async def check_db_table_exists(session: AsyncSession = Depends(get_async_session)):
    try:
        result = await session.execute(text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users')"))
        table_exists = result.scalar()

        logger.info("Database table check successful. Table exists: %s", table_exists)

        return {"table_exists": table_exists}
    except Exception as e:
        logger.error("Error occurred while checking database table existence")
        raise HTTPException(status_code=500, detail=str(e))



