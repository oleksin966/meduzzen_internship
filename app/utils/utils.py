from passlib.context import CryptContext
from sqlalchemy import select

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def hash_password(password: str) -> str:
    return pwd_context.hash(password)

class Paginate:
    def __init__(self, db: None, model: None, offset: int | None = None, limit: int | None = None):
        self.db = db
        self.model = model
        self.offset = offset
        self.limit = limit

    async def fetch_results(self):
        statement = select(self.model).offset(self.offset).limit(self.limit)
        result = await self.db.execute(statement)
        return result.scalars().all()