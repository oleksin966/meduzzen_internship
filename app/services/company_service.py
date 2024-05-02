from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, exists
from db.models import User, Company, Invitation, Request, CompanyUser
from typing import List, Dict
from fastapi import Depends, HTTPException
from schemas.company_schema import CompanySchema
from schemas.user_schema import UserSchema, UserId
from utils.utils import Paginate, get_user_by_id, get_company_by_id, get_owned_company
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
        user: UserId
    ):
        self.session = session
        self.auth_user = user


    async def send_invitation_to_user(self, user_id, company_id):
        '''Владелец должен иметь возможность отправить приглашение в свою 
        компанию неограниченное количество других пользователей'''

        owner_id = self.auth_user.id

        user = await get_user_by_id(self.session, user_id)
        
        # get all own companies of current auth user
        companies = await get_owned_company(self.session, owner_id)

        # get the company to which the owner sent a invite
        company = next((com for com in companies if com.id == company_id), None)
        
        if user and company:
            subquery = select(Invitation).where(
                    (Invitation.company_id == company_id) &
                    (Invitation.user_id == user_id) &
                    (Invitation.status == "pending")
                )

            invitation_exists = await self.session.execute(subquery)
            invitation_exists = invitation_exists.scalar()

            if not invitation_exists:
                invitation = Invitation(company_id=company_id, user_id=user_id, owner_id=owner_id, status="pending")
                self.session.add(invitation)
                await self.session.commit()

                result = {
                    "id": invitation.id,
                    "owner": self.auth_user.username,
                    "user": user.username,
                    "company": company.name,
                    "status":"pending",
                    "action":"Invitation user to company"
                }
                return result
                #return invitation
            else:
                raise HTTPException(status_code=404, detail="Invitation already exists.")
        else:
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            if not company:
                raise HTTPException(status_code=404, detail="Company not found")


    async def cancel_invitation(self, invitation_id):
        '''Владалец должен иметь возможность отменить свое приглашение'''

        owner_id = self.auth_user.id

        invitation = await self.session.get(Invitation, invitation_id)

        if invitation is None:
            raise HTTPException(status_code=404, detail="Invitation not found")

        if owner_id != invitation.owner_id: 
            raise HTTPException(status_code=403, detail="You are not the owner of this invitation")

        await self.session.delete(invitation)
        await self.session.commit()

        return {"message": "Invitation canceled successfully"}

    async def accept_request_from_user(self, request_id):
        '''Владелец должен иметь возможность принять запрос на вступление в компанию'''
        
        # get owner of request 
        owner_id = self.auth_user.id

        # get request for ID
        request = await self.session.get(Request, request_id)

        if request is None:
            raise HTTPException(status_code=404, detail="Request not found")

        # get all own companies of current auth user
        companies = await get_owned_company(self.session, owner_id)

        # get the company to which the user submitted a request
        company = next((com for com in companies if com.id == request.company_id), None)
        
        if company:
            subquery = select(CompanyUser).where(
                    (CompanyUser.company_id == company.id) &
                    (CompanyUser.user_id == request.owner_id)
                ) 

            company_user_exists = await self.session.execute(subquery)
            company_user_exists = company_user_exists.scalar()

            if not company_user_exists: # check if user exist in company
                await self.session.delete(request) # delete request & add user to company
                await self.session.commit()

                company_user = CompanyUser(user_id=request.owner_id, company_id=company.id)
                self.session.add(company_user)
                await self.session.commit()
            else:
                raise HTTPException(status_code=404, detail="User already exist in Company")
        else:
            raise HTTPException(status_code=403, detail="This request is not for your company")

        result = {
            "id": company_user.id,
            "owner": self.auth_user.username,
            "user": request.owner_id,
            "company": company.name,
            "status":"accepted",
            "action":"Accept User in company"
        }
        return result
        #return company_user

    async def decline_request_from_user(self, request_id):
        '''Владелец должен иметь возможность отклонить запрос на вступление в компанию'''
        
        # get owner of request 
        owner_id = self.auth_user.id

        request = await self.session.get(Request, request_id)

        if request is None:
            raise HTTPException(status_code=404, detail="Request not found")

        # get all own companies of current auth user
        companies = await get_owned_company(self.session, owner_id)

        # get the company to which the user submitted a request
        company = next((com for com in companies if com.id == request.company_id), None)


        if company:
            await self.session.delete(request) # cancel request 
            await self.session.commit()
        else:
            raise HTTPException(status_code=403, detail="This request is not for your company")

        result = {
            "id": request.id,
            "owner": self.auth_user.username,
            "user": request.owner_id,
            "company": company.name,
            "status":"declined",
            "action":"Decline User's request"
        }
        return result
        #return {"deleted request": request.id}

    # # user actions
    async def accept_invite_from_owner(self, invitation_id):
        '''Пользователь должен иметь возможность принять приглашение в Компанию - 
        после чего последует автоматическое вступление пользователя в участники группы'''
        user_id = self.auth_user.id

        invitation = await self.session.get(Invitation, invitation_id)

        if invitation is None:
                raise HTTPException(status_code=404, detail="Invitation not found")


        # get all own companies of current auth user
        companies = await get_owned_company(self.session, invitation.user_id)

        # get the company to which the user submitted a request
        company = next((com for com in companies if com.id == invitation.company_id), None)
        
        if company:
            subquery = select(CompanyUser).where(
                    (CompanyUser.company_id == company.id) &
                    (CompanyUser.user_id == invitation.user_id)
                ) 

            company_user_exists = await self.session.execute(subquery)
            company_user_exists = company_user_exists.scalar()

            if not company_user_exists: # check if user exist in company
                await self.session.delete(invitation) # delete invitation & add user to company
                await self.session.commit()

                company_user = CompanyUser(user_id=invitation.user_id, company_id=company.id)
                self.session.add(company_user)
                await self.session.commit()
            else:
                raise HTTPException(status_code=404, detail="User already exist in Company")
        else:
            raise HTTPException(status_code=403, detail="This invitation is not your")

        result = {
            "id": invitation.id,
            "owner": self.auth_user.username,
            "user": invitation.user_id,
            "company": company.name,
            "status":"accept",
            "action":"User accept invitation to company"
        }
        return result
        #return {"deleted request": request.id}



    async def decline_invitation(self, invitation_id):
        '''Пользователь должен иметь возможность отклонить приглашение в Компанию'''
        
        user_id = self.auth_user.id

        invitation = await self.session.get(Invitation, invitation_id)

        if invitation is None:
            raise HTTPException(status_code=404, detail="Invitation not found")

        if user_id != invitation.user_id: 
            raise HTTPException(status_code=403, detail="This invitation not for you")

        await self.session.delete(invitation)
        await self.session.commit()

        result = {
            "id": invitation.id,
            "owner": invitation.owner_id,
            "user": invitation.user_id,
            "status":"decline",
            "action":"User decline invitation to company"
        }
        return result
        #return {"deleted request": invitation.id}




    async def send_request(self, company_id):
        '''Пользователь должен иметь возможность отправить запрос 
        на вступление в компанию. Список компаний неограничен'''
        
        user_id = self.auth_user.id
        company = await get_company_by_id(self.session, company_id)

        if company:

            if company.owner_id == user_id:
                raise HTTPException(status_code=400, detail="You already own this company")

            subquery = select(Request).where(
                (Request.company_id == company_id) &
                (Request.owner_id == user_id) &
                (Request.status == "pending")
            )

            request_exists = await self.session.execute(subquery)
            request_exists = request_exists.scalar()
            if not request_exists:
                request = Request(company_id=company_id, owner_id=user_id, status="pending")
                self.session.add(request)
                await self.session.commit()
                result = {
                    "id": request.id,
                    "owner": self.auth_user.username,
                    "company": company.name,
                    "status":"pending",
                    "action":"Request user to company"
                }
                return result
                #return invitation
            else:
                raise HTTPException(status_code=400, detail="Request already exists.")
        else:
            raise HTTPException(status_code=404, detail="Company not found")


    async def cancel_sent_request(self, request_id):
        '''Пользователь должен иметь возможность отменить свой отправленный запрос 
        на вступление в компанию'''

        user_id = self.auth_user.id

        request = await self.session.get(Request, request_id)

        if request is None:
            raise HTTPException(status_code=404, detail="Request not found")

        if user_id != request.owner_id: 
            raise HTTPException(status_code=403, detail="You are not the owner of this request")

        await self.session.delete(request)
        await self.session.commit()

        return {"message": "Request canceled successfully"}



    async def remove_user_from_company(self, user_id, company_id):
        '''Владелец должен иметь возможность исключать пользователей из компании'''
        owner_id = self.auth_user.id
        
        companies = await get_owned_company(self.session, owner_id)

        company = next((com for com in companies if com.id == company_id), None)
        print("++++++++",company)
        if company:
            subquery = select(CompanyUser).where(
                    (CompanyUser.company_id == company_id) &
                    (CompanyUser.user_id == user_id)
                ) 

            company_user_exists = await self.session.execute(subquery)
            company_user_exists = company_user_exists.scalar()
            if company_user_exists:
                await self.session.delete(company_user_exists)
                await self.session.commit()
                return {"message": f"User with id {user_id} has been removed from the company"}
            else:
                raise HTTPException(status_code=404, detail="User is not a member of the company")
        else:
            raise HTTPException(status_code=404, detail="Company not found or user is not the owner of the company")


    async def leave_company(self, company_id):
        '''Пользователь должен иметь возможность выйти из компании'''
        user_id = self.auth_user.id

        company = await self.session.get(Company, company_id)

        if company:
            subquery = select(CompanyUser).where(
                (CompanyUser.company_id == company_id) &
                (CompanyUser.user_id == user_id)
            )
            company_user_exists = await self.session.execute(subquery)
            company_user_exists = company_user_exists.scalar()

            if company_user_exists:
                await self.session.delete(company_user_exists)
                await self.session.commit()
                return {"message": "You have left the company"}
            else:
                raise HTTPException(status_code=403, detail="You are not a member of the company")
        else:
            raise HTTPException(status_code=404, detail="Company does not exist")
    
    # #endpoints from requierements
    async def user_list_requests(self):
        '''Реализовать ендпоинт с помощью которого каждый User должен 
        иметь возможность посмотреть список своих запросов в компании'''
        user_id = self.auth_user.id



    # async def user_list_invitations(self):
    #     pass

    # async def list_invitations_in_company(self):
    #     pass

    # async def list_requests_in_company(self):
    #     pass

    # async def list_users_in_company(self):
    #     pass





