from functools import wraps
from typing import Callable
from logging import getLogger

logger = getLogger(__name__)
def exception_handler(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            logger.info("Function executed successfully")  # Log success
            return result
        except Exception as e:
            logger.error("ERROR OCCURED: %s", e)
    return wrapper