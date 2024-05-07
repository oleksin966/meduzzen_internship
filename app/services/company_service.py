from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, exists
from sqlalchemy.orm import joinedload
from db.models import User, Company, Invitation, Request, CompanyUser
from typing import List, Dict
from fastapi import Depends, HTTPException
from schemas.company_schema import CompanySchema
from schemas.user_schema import UserId
from utils.utils import Paginate
from utils.decorators import exception_handler
from utils.exceptions import (UserNotFoundException, 
    RequestOwnershipException, 
    InvitationOwnershipException, 
    NotOwnerCompanyException, 
    RequestAlreadySentException, 
    RequestNotFoundException, 
    InvitationNotFoundException, 
    CompanyNotFoundException, 
    AlreadyMemberException, 
    InvitationAlreadySentException)

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
        where = self.model.owner_id == self.user.id
        paginator = Paginate(self.session, self.model, page, where=where)
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
        user: UserId
    ):
        self.session = session
        self.auth_user = user


    async def send_invitation(self, user_id, company_id):
        '''Владелец должен иметь возможность отправить приглашение в свою 
        компанию неограниченное количество других пользователей'''

        user = await self.session.get(User, user_id)
        if not user:
            raise UserNotFoundException()

        # Check if the company is owned auth user or company exist
        statement = select(Company).where((Company.id == company_id) & (Company.owner_id == self.auth_user.id))
        company = await self.session.execute(statement)
        company = company.scalar_one_or_none()
        if not company:
            raise CompanyNotFoundException()

        # Check if the user is already a member of the company
        statement = select(exists().where((CompanyUser.user_id == user_id) & (CompanyUser.company_id == company_id)))
        user_in_company = await self.session.execute(statement)
        user_in_company = user_in_company.scalar()
        if user_in_company:
            raise AlreadyMemberException()

        # Check if exist invitation
        statement = select(Invitation).where((Invitation.company_id == company_id) & (Invitation.user_id == user_id))
        existing_invitation = await self.session.execute(statement)
        existing_invitation = existing_invitation.scalar_one_or_none()

        if existing_invitation:
            raise InvitationAlreadySentException()

        invitation = Invitation(company_id=company_id, user_id=user_id)

        self.session.add(invitation)

        await self.session.commit()
        await self.session.refresh(invitation, ['company', 'user'])
        
        return invitation


    async def cancel_invitation(self, invitation_id):
        '''Владалец должен иметь возможность отменить свое приглашение'''

        invitation = await self.session.get(
            Invitation, 
            invitation_id, 
            options=[
                joinedload(Invitation.company),
                joinedload(Invitation.user)
            ]
        )
        if invitation is None:
            raise InvitationNotFoundException()

        company = await self.session.get(Company, invitation.company_id)
        if self.auth_user.id != company.owner_id: 
            raise NotOwnerCompanyException()

        await self.session.delete(invitation)
        await self.session.commit()
        return invitation

    async def accept_request(self, request_id):
        '''Владелец должен иметь возможность принять запрос на вступление в компанию'''
        
        request = await self.session.get(Request, request_id)
        if request is None:
            raise RequestNotFoundException()

        company = await self.session.get(Company, request.company_id)
        if self.auth_user.id != company.owner_id: 
            raise NotOwnerCompanyException()


        await self.session.delete(request) # delete request & add user to company
        await self.session.commit()

        company_user = CompanyUser(user_id=request.user_id, company_id=request.company_id)
        self.session.add(company_user)
        await self.session.commit()
        await self.session.refresh(company_user, ['company', 'user'])
        return company_user

    async def reject_request(self, request_id):
        '''Владелец должен иметь возможность отклонить запрос на вступление в компанию'''

        request = await self.session.get(
            Request, 
            request_id,
            options=[
                joinedload(Request.company),
                joinedload(Request.user)
            ])
        if request is None:
            raise RequestNotFoundException()

        company = await self.session.get(Company, request.company_id)
        if self.auth_user.id != company.owner_id: 
            raise NotOwnerCompanyException()

        await self.session.delete(request)
        await self.session.commit()
   
        return request







    # user actions
    async def accept_invitation(self, invitation_id):
        '''Пользователь должен иметь возможность принять приглашение в Компанию - 
        после чего последует автоматическое вступление пользователя в участники группы'''

        invitation = await self.session.get(Invitation, invitation_id)
        if invitation is None:
            raise InvitationNotFoundException()

        if self.auth_user.id != invitation.user_id:
            raise InvitationOwnershipException()

        await self.session.delete(invitation) # delete invitation & add user to company
        await self.session.commit()

        company_user = CompanyUser(user_id=invitation.user_id, company_id=invitation.company_id)
        self.session.add(company_user)
        await self.session.commit()
        await self.session.refresh(company_user, ['company', 'user'])

        return company_user


    async def reject_invitation(self, invitation_id):
        '''Пользователь должен иметь возможность отклонить приглашение в Компанию'''
        
        invitation = await self.session.get(
            Invitation, 
            invitation_id,
            options=[
                joinedload(Invitation.company),
                joinedload(Invitation.user)
            ])
        if invitation is None:
            raise InvitationNotFoundException()

        if self.auth_user.id != invitation.user_id:
            raise InvitationOwnershipException()

        await self.session.delete(invitation)
        await self.session.commit()

        return invitation



    async def send_request(self, company_id):
        '''Пользователь должен иметь возможность отправить запрос 
        на вступление в компанию. Список компаний неограничен'''
        
        user_id = self.auth_user.id

        # check if company exit AND if user owner company
        company = await self.session.get(Company, company_id)
        if not company or company.owner_id == user_id:
            raise CompanyNotFoundException()


        # Check if the user is already a member of the company
        statement = select(exists().where((CompanyUser.user_id == user_id) & (CompanyUser.company_id == company_id)))
        result = await self.session.execute(statement)
        user_in_company = result.scalar()
        if user_in_company:
            raise AlreadyMemberException()

        # Check if exist request
        statement = select(Request).where((Request.company_id == company_id) & (Request.user_id == user_id))
        result = await self.session.execute(statement)
        existing_request = result.scalar_one_or_none()
        if existing_request:
            raise RequestAlreadySentException()

        request = Request(company_id=company_id, user_id=user_id)
        self.session.add(request)
        await self.session.commit()
        await self.session.refresh(request, ['company', 'user'])

        return request


    async def cancel_request(self, request_id):
        '''Пользователь должен иметь возможность отменить свой отправленный запрос 
        на вступление в компанию'''

        request = await self.session.get(
            Request, 
            request_id,
            options=[
                joinedload(Request.company),
                joinedload(Request.user)
            ])
        if request is None:
            raise RequestNotFoundException()

        if self.auth_user.id != request.user_id: 
            raise RequestOwnershipException()

        await self.session.delete(request)
        await self.session.commit()
        
        return request



    async def remove_user_from_company(self, user_id, company_id):
        '''Владелец должен иметь возможность исключать пользователей из компании'''

        company = await self.session.get(Company, company_id)
        if not company:
            raise CompanyNotFoundException()

        if self.auth_user.id != company.owner_id: 
            raise NotOwnerCompanyException()

        # Check if the user is already a member of the company
        statement = (
            select(CompanyUser)
            .options(
                joinedload(CompanyUser.company),
                joinedload(CompanyUser.user)
            )
            .where(
                (CompanyUser.user_id == user_id) & 
                (CompanyUser.company_id == company_id)
            )
        )
        result = await self.session.execute(statement)
        user_in_company = result.scalar_one_or_none()
        if not user_in_company:
            raise UserNotFoundException()

       # Remove the user from the company
        delete_statement = (
            delete(CompanyUser)
            .where((CompanyUser.user_id == user_id) & (CompanyUser.company_id == company_id))
        )

        await self.session.execute(delete_statement)
        await self.session.commit()

        return user_in_company





    async def leave_company(self, company_id):
        '''Пользователь должен иметь возможность выйти из компании'''

        company = await self.session.get(Company, company_id)
        if not company:
            raise CompanyNotFoundException()

        statement = (
            select(CompanyUser)
            .options(
                joinedload(CompanyUser.company),
                joinedload(CompanyUser.user)
            )
            .where(
                (CompanyUser.user_id == self.auth_user.id) & 
                (CompanyUser.company_id == company_id)
            )
        )
        result = await self.session.execute(statement)
        user_in_company = result.scalar_one_or_none()
        if not user_in_company:
            raise UserNotFoundException()

       # Remove the user from the company
        delete_statement = (
            delete(CompanyUser)
            .where((CompanyUser.user_id == self.auth_user.id) & (CompanyUser.company_id == company_id))
        )

        await self.session.execute(delete_statement)
        await self.session.commit()

        return user_in_company

    
    #endpoints from requierements
    async def user_list_requests(self, page):
        '''Реализовать ендпоинт с помощью которого каждый User должен 
        иметь возможность посмотреть список своих запросов в компании'''

        options = [joinedload(Request.company), joinedload(Request.user)]
        where = Request.user_id == self.auth_user.id

        paginator = Paginate(self.session, Request, page, options=options, where=where)
        paginate_requests = await paginator.fetch_results()
        return paginate_requests



    async def user_list_invitations(self, page):
        '''Реализовать ендпоинт с помощью которого каждый User должен 
        иметь возможность посмотреть список приглашений его в компани'''

        options = [joinedload(Invitation.company), joinedload(Invitation.user)]
        where = Invitation.user_id == self.auth_user.id

        paginator = Paginate(self.session, Invitation, page, options=options, where=where)
        paginate_invitations = await paginator.fetch_results()
        return paginate_invitations


    async def owner_list_invitations(self, page):
        '''Реализовать еднпоинт с помощью которого Владелец 
        компании может увидеть список приглашенных пользователей'''

        options = [joinedload(Invitation.company), joinedload(Invitation.user)]
        where = Invitation.company.has(owner_id=self.auth_user.id)

        paginator = Paginate(self.session, Invitation, page, options=options, where=where)
        paginate_invitations = await paginator.fetch_results()
        return paginate_invitations

    async def requests_in_company(self, page, company_id):
        '''Реализовать ендпоинт с помощью которого Владелец компании 
        может увидеть список запросов на вступление в компанию'''

        company = await self.session.get(Company, company_id)
        if not company or company.owner_id != self.auth_user.id:
            raise NotOwnerCompanyException()

        options = [joinedload(Request.company), joinedload(Request.user)]
        where = Request.company_id == company_id

        paginator = Paginate(self.session, Request, page, options=options, where=where)
        paginate_requests = await paginator.fetch_results()
        return paginate_requests

    async def users_in_company(self, page, company_id):
        '''Реализовать ендпоинт с помощью которого можно увидеть 
        список пользователей в компании'''

        company = await self.session.get(Company, company_id)
        if not company:
            raise CompanyNotFoundException()

        options = [joinedload(CompanyUser.user)]
        where = CompanyUser.company_id == company_id

        paginator = Paginate(self.session, CompanyUser, page, options=options, where=where)
        paginate_requests = await paginator.fetch_results()
        return paginate_requests



