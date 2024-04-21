from passlib.context import CryptContext
from sqlalchemy import select

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def hash_password(password: str) -> str:
    return pwd_context.hash(password)

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

