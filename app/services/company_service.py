from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from db.models import User, Company, Invitation, Request, CompanyUser
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
		statement = select(self.model) \
					.where(self.model.owner_id == self.user.id)
		paginator = Paginate(self.session, statement, page)
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


class CompanyActions:
	def __init__(
		self, 
		session: AsyncSession, 
		#user: UserId
	):
		self.session = session
		# self.company = Company
		# self.auth_user = user

	# owner actions
	async def send_invitation(self, user_id, company_id):
		'''Владелец должен иметь возможность отправить приглашение в свою 
		компанию неограниченное количество других пользователей'''
		pass

	async def cancel_invitation(self, invitation_id):
		'''Владалец должен иметь возможность отменить свое приглашение'''
		pass

	async def accept_request_from_user(self, user_id, request_id):
		'''Владелец должен иметь возможность принять запрос на вступление в компанию'''
		pass

	async def decline_request_from_user(self, user_id, request_id):
		'''Владелец должен иметь возможность отклонить запрос на вступление в компанию'''
		pass

	# user actions
	async def accept_invite_from_owner(self, invitation_id):
		'''Пользователь должен иметь возможность принять приглашение в Компанию - 
		после чего последует автоматическое вступление пользователя в участники группы'''
		pass

	async def decline_invitation(self, invitation_id):
		'''Пользователь должен иметь возможность отклонить приглашение в Компанию'''
		pass

	async def send_request(self, company_id):
		'''Пользователь должен иметь возможность отправить запрос 
		на вступление в компанию. Список компаний неограничен'''
		pass

	async def decline_sent_request(self, request_id):
		'''Пользователь должен иметь возможность отменить свой отправленный запрос 
		на вступление в компанию'''
		pass



	async def remove_user_from_company(self, user_id, company_id):
		'''Владелец должен иметь возможность исключать пользователей из компании'''
		pass

	async def leave_company(self, company_id):
		'''Пользователь должен иметь возможность выйти из компании'''
		pass


	#endpoints from requierements
	async def user_list_requests(self):
		pass

	async def user_list_invitations(self):
		pass

	async def list_invitations_in_company(self):
		pass

	async def list_requests_in_company(self):
		pass

	async def list_users_in_company(self):
		pass


