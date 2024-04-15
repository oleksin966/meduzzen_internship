from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import OperationalError
from sqlalchemy import text

from db.database import get_async_session
from db.redis import get_redis_client
from aioredis import Redis

router_connects = APIRouter()

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