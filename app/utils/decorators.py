from functools import wraps
from typing import Callable
from logging import getLogger
from db.models import Company
from utils.exceptions import CompanyNotFoundException, NotPermission
from sqlalchemy.orm import joinedload

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


def check_if_user_or_owner(func):
    @wraps(func)
    async def wrapper(self, company_id: int, *args, **kwargs):
        company = await self.session.get(
            Company, 
            company_id,
            options=[
                joinedload(Company.company_users)
            ]
        )
        if company is None:
            raise CompanyNotFoundException()

        admin = None
        owner = company.owner_id == self.user.id
        for user in company.company_users:
            if user.user_id == self.user.id and user.is_administrator:
                admin = user
                break

        if not owner and not admin:
            raise NotPermission()

        return await func(self, company_id, *args, **kwargs)
    return wrapper