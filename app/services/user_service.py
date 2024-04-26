from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, delete, update
from schemas.user_schema import UserSignUp, UserSignUpEmail, UserSchema, UserList, UserUpdate
from db.models import User
from typing import List, Dict
from utils.utils import hash_password, Paginate
from utils.decorators import exception_handler


class UserServiceCrud:
	def __init__(self, session: AsyncSession):
		self.session = session
		self.model = User

	@exception_handler
	async def get_all_users(self, page: int) -> List[User]:
		get_users = await self.session.execute(select(self.model))
		paginator = Paginate(self.session, self.model, page)
		paginate_users = await paginator.fetch_results()
		return paginate_users

	@exception_handler
	async def get_user_by_id(self, user_id: int) -> User:
		get_user = await self.session.get(User, user_id)
		return get_user

	@exception_handler
	async def create_user(self, user: UserSignUp) -> User:
	    model_dump = user.model_dump()
	    model_dump["password"] = hash_password(model_dump["password"])
	    new_user = User(**model_dump)
	    self.session.add(new_user)

	    await self.session.commit()
	    await self.session.refresh(new_user)
	    return new_user


	@exception_handler
	async def update_user(self, user_id: int, data: Dict) -> User:
		statement = (
            update(self.model)
            .where(self.model.id == user_id)
            .values(**data)
            .returning(self.model)
        )
		updating = await self.session.execute(statement)
		updated_user = updating.scalar_one()
        
		await self.session.commit()
		await self.session.refresh(updated_user)
		return updated_user

	@exception_handler
	async def delete_user(self, user_id: int) -> User:
		get_user = await self.session.get(self.model, user_id)
		await self.session.delete(get_user)
		await self.session.commit()
		return get_user

