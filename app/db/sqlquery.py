from abc import ABC, abstractmethod
from typing import Dict, Union
from sqlalchemy import select, insert, delete, update
from db.database import async_session


# Interface of CRUD Class
class UserCrudInterface(ABC):
    @abstractmethod
    async def get_all_users():
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_id(pk: Union[str, int]):
        raise NotImplementedError

    @abstractmethod
    async def create(): #SignUp
        raise NotImplementedError

    @abstractmethod
    async def update(pk: Union[str, int], data: Dict):
        raise NotImplementedError

    @abstractmethod
    async def delete(pk: Union[str, int]):
        raise NotImplementedError

# CRUD Class for users
class UsersSqlQuery(UserCrudInterface):
    def __init__(self, model: None):
        self.model = model

    async def get_all_users(self):
        pass # implemented with Paginate in file routers/users.py

    async def get_user_by_id(self, pk: Union[str, int]) -> Dict:
        async with async_session() as session:
            statement = select(self.model).where(self.model.id == pk)
            result = await session.execute(statement)
            result_data = [row[0] for row in result.all()]
            return result_data[0]

    async def create(self, data: Dict) -> int:
        async with async_session() as session:
            statement = insert(self.model).values(**data).returning(self.model.id)
            result = await session.execute(statement)
            await session.commit()
            return result.scalar_one()

    async def update(self, pk: int, data: Dict):
        async with async_session() as session:
            statement = (
                update(self.model)
                .where(self.model.id == pk)
                .values(**data)
                .returning(self.model.id)
            )
            result = await session.execute(statement)
            await session.commit()
            return result.scalar()

    async def delete(self, pk: Union[str, int]) -> int:
        async with async_session() as session:
            statement = (
                delete(self.model).where(self.model.id == pk).returning(self.model.id)
            )
            result = await session.execute(statement)
            await session.commit()
            return result.scalar_one()