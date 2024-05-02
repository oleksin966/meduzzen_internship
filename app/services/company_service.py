from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from db.models import User, Company
from typing import List, Dict
from fastapi import Depends
from schemas.company_schema import CompanySchema
from schemas.user_schema import UserSchema, UserId
from utils.utils import Paginate
from utils.decorators import exception_handler

class CompanyServiceCrud:
	def __init__(
		self, 
		session: AsyncSession, 
		user: UserId
	):
		self.session = session
		self.model = Company
		self.user = user

	@exception_handler
	async def get_all_companies(self, page: int) -> List[CompanySchema]:
		filterr = self.model.owner_id == self.user.id
		paginator = Paginate(self.session, self.model, page, filterr)
		paginate_company = await paginator.fetch_results()
		return paginate_company

	@exception_handler
	async def get_company_by_id(self, company_id: int) -> CompanySchema:
		statement = select(self.model) \
					.where((self.model.id == company_id) & (self.model.owner_id == self.user.id))
		company = await self.session.execute(statement)
		return company.scalar_one_or_none()

	@exception_handler
	async def create_company(self, company: CompanySchema) -> CompanySchema:
		model_dump = company.model_dump()
		model_dump["owner_id"] = self.user.id
		new_company = Company(**model_dump)
		self.session.add(new_company)

		await self.session.commit()
		await self.session.refresh(new_company)
		return new_company

	@exception_handler
	async def update_company(self, company_id: int, data: Dict) -> CompanySchema:
		statement = (
            update(self.model)
            .where(self.model.id == company_id)
            .values(**data)
            .returning(self.model)
        )
		updating = await self.session.execute(statement)
		updated_user = updating.scalar_one()
        
		await self.session.commit()
		await self.session.refresh(updated_user)
		return updated_user

	@exception_handler
	async def delete_company(self, company_id: int) -> CompanySchema:
		get_company = await self.session.get(self.model, company_id)
		await self.session.delete(get_company)
		await self.session.commit()
		return get_company



