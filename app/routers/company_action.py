from fastapi import APIRouter, Depends, HTTPException, Path
from db.database import get_async_session
from schemas.user_schema import UserId
from schemas.company_schema import (CompanyUsers, 
    CompanyCreate, 
    LeaveCompany, 
    DeleteFromCompany, 
    RequestCancel, 
    RequestSent, 
    InvitationAccept, 
    InvitationReject, 
    RequestAccept, 
    Requestreject, 
    CompanyActionSchema, 
    InvitationSent, 
    InvitationCancel,
    AddAdmin,
    RemoveAdmin,
    UserIsNotAdmin)
from utils.auth import get_current_user
from utils.exceptions import (UserNotFoundException, 
    InvitationOwnershipException, 
    RequestOwnershipException, 
    NotOwnerCompanyException, 
    RequestAlreadySentException, 
    RequestNotFoundException, 
    InvitationNotFoundException, 
    CompanyNotFoundException, 
    AlreadyMemberException, 
    InvitationAlreadySentException)
from sqlalchemy.ext.asyncio import AsyncSession
from services.company_service import CompanyActions
from typing import List, Union

router_company_action = APIRouter(prefix="/action")





# admin process
@router_company_action.patch('/add_admin/{user_id}', summary="Owner add admin to company", response_model=AddAdmin)
async def add_admin(
        company_id: int,
        user_id: int = Path(..., title="The ID of user's"),
        session: AsyncSession = Depends(get_async_session),
        user: UserId = Depends(get_current_user)
    ):
    '''Владалец должен иметь возможность добавлять администраторов в свою компанию'''
    try:
        company_actions = CompanyActions(session, user)
        return await company_actions.add_admin(user_id, company_id)
    except UserNotFoundException:
        raise HTTPException(status_code=404, detail="User doesnt exist in your company.")
    except NotOwnerCompanyException:
        raise HTTPException(status_code=403, detail="You are not the owner of this company.")

@router_company_action.patch('/remove_admin/{user_id}', summary="Owner remove admin from company", response_model=Union[RemoveAdmin, UserIsNotAdmin])
async def remove_admin(
        company_id: int,
        user_id: int = Path(..., title="The ID of admin's"),
        session: AsyncSession = Depends(get_async_session),
        user: UserId = Depends(get_current_user)
    ):
    '''Владалец должен иметь возможность разжаловать администратора в компании'''
    try:
        company_actions = CompanyActions(session, user)
        return await company_actions.remove_admin(user_id, company_id)
    except UserNotFoundException:
        raise HTTPException(status_code=404, detail="User doesnt exist in your company.")
    except NotOwnerCompanyException:
        raise HTTPException(status_code=403, detail="You are not the owner of this company.")

@router_company_action.get('/admins/{company_id}', summary="Admins in company", response_model=List[CompanyUsers])
async def list_admins(
        page: int = 1,
        company_id: int = Path(..., title="The ID of company"),
        session: AsyncSession = Depends(get_async_session),
        user: UserId = Depends(get_current_user)  
    ):
    '''Eндпоинт с помощью которого можно увидеть список админов в компании'''
    try:
        company_actions = CompanyActions(session, user)
        return await company_actions.list_admins(page, company_id)
    except CompanyNotFoundException:
        raise HTTPException(status_code=404, detail="Company not found")







# owner actions
@router_company_action.post('/invite/{user_id}', summary="Owner invite User to company", response_model=InvitationSent)
async def send_invitation(
	    company_id: int,
        user_id: int = Path(..., title="The ID of User"),
        session: AsyncSession = Depends(get_async_session),
        user: UserId = Depends(get_current_user)
    ):
    '''Владелец должен иметь возможность отправить приглашение в свою 
    компанию неограниченное количество других пользователей'''
    try:
        company_actions = CompanyActions(session, user)
        sent_invitation = await company_actions.send_invitation(user_id, company_id)
        return sent_invitation
    except UserNotFoundException:
        raise HTTPException(status_code=404, detail="User not found.")
    except CompanyNotFoundException:
        raise HTTPException(status_code=404, detail="You are not the owner of this company or company not found.")
    except AlreadyMemberException:
        raise HTTPException(status_code=400, detail="The user is already a member of this company.")
    except InvitationAlreadySentException:
        raise HTTPException(status_code=400, detail="An invitation has already been sent to this user for this company.")


@router_company_action.delete('/cancel/{invitation_id}', summary="Owner cancel invite User to company", response_model=InvitationCancel)
async def cancel_invitation(
	invitation_id: int = Path(..., title="The ID of cancel invitation"),
        session: AsyncSession = Depends(get_async_session),
        user: UserId = Depends(get_current_user)   
    ):
    '''Владалец должен иметь возможность отменить свое приглашение'''
    try:
        company_actions = CompanyActions(session, user)
        return await company_actions.cancel_invitation(invitation_id)
    except InvitationNotFoundException:
        raise HTTPException(status_code=404, detail="Invitation not found.")
    except NotOwnerCompanyException:
        raise HTTPException(status_code=403, detail="You are not the owner of this company.")


@router_company_action.post('/accept/{request_id}', summary="Owner accept request from User", response_model=RequestAccept)
async def accept_request(
        request_id: int = Path(..., title="The ID of accept request to company"),
        session: AsyncSession = Depends(get_async_session),
        user: UserId = Depends(get_current_user)   
    ):
    '''Владелец должен иметь возможность принять запрос на вступление в компанию'''
    try:
        company_actions = CompanyActions(session, user)
        return await company_actions.accept_request(request_id)
    except RequestNotFoundException:
        raise HTTPException(status_code=404, detail="Request not found.")
    except NotOwnerCompanyException:
        raise HTTPException(status_code=403, detail="This request not for your company.")


@router_company_action.delete('/reject/{request_id}', summary="Owner decline request from User", response_model=Requestreject)
async def reject_request(
        request_id: int = Path(..., title="The ID of cancel request to company"),
        session: AsyncSession = Depends(get_async_session),
        user: UserId = Depends(get_current_user)   
    ):
    '''Владелец должен иметь возможность отклонить запрос на вступление в компанию'''
    try:
        company_actions = CompanyActions(session, user)
        return await company_actions.reject_request(request_id)
    except RequestNotFoundException:
        raise HTTPException(status_code=404, detail="Request not found.")
    except NotOwnerCompanyException:
        raise HTTPException(status_code=403, detail="This request not for your company.")







# user actions
@router_company_action.post('/accept_invite/{invitation_id}', summary="User accept invitation from Owner", response_model=InvitationAccept)
async def accept_invitation(
        invitation_id: int = Path(..., title="The ID of accepted invitation"),
        session: AsyncSession = Depends(get_async_session),
        user: UserId = Depends(get_current_user)   
    ):
    '''Пользователь должен иметь возможность принять приглашение в Компанию - 
    после чего последует автоматическое вступление пользователя в участники группы'''
    try:
        company_actions = CompanyActions(session, user)
        return await company_actions.accept_invitation(invitation_id)
    except InvitationNotFoundException:
        raise HTTPException(status_code=404, detail="Invitation not found.")
    except InvitationOwnershipException:
        raise HTTPException(status_code=403, detail="This invitation not for you.")


@router_company_action.delete('/reject_invite/{invitation_id}', summary="User decline invitation from Owner", response_model=InvitationReject)
async def reject_invitation(
        invitation_id: int = Path(..., title="The ID of rejected invitation"),
        session: AsyncSession = Depends(get_async_session),
        user: UserId = Depends(get_current_user)  
    ):
    '''Пользователь должен иметь возможность отклонить приглашение в Компанию'''
    try:
        company_actions = CompanyActions(session, user)
        return await company_actions.reject_invitation(invitation_id)
    except InvitationNotFoundException:
        raise HTTPException(status_code=404, detail="Invitation not found.")
    except InvitationOwnershipException:
        raise HTTPException(status_code=403, detail="This invitation not for you.")


@router_company_action.post('/request/{company_id}', summary="User send request to company", response_model=RequestSent)
async def send_request(
		company_id: int = Path(..., title="The ID of requested company"),
        session: AsyncSession = Depends(get_async_session),
        user: UserId = Depends(get_current_user)   
    ):
    '''Пользователь должен иметь возможность отправить запрос 
    на вступление в компанию. Список компаний неограничен'''
    try:
        company_actions = CompanyActions(session, user)
        return await company_actions.send_request(company_id)
    except CompanyNotFoundException:
        raise HTTPException(status_code=404, detail="Company not found.")
    except AlreadyMemberException:
        raise HTTPException(status_code=400, detail="You already a member of this company.")
    except RequestAlreadySentException:
        raise HTTPException(status_code=400, detail="A request has already been sent to this company.")


@router_company_action.delete('/cancel_request/{request_id}', summary="User cancel request to company", response_model=RequestCancel)
async def cancel_request(
		request_id: int = Path(..., title="The ID of cancel request to company"),
        session: AsyncSession = Depends(get_async_session),
        user: UserId = Depends(get_current_user)   
    ):
    '''Пользователь должен иметь возможность отменить свой отправленный запрос 
    на вступление в компанию'''
    try:
        company_actions = CompanyActions(session, user)
        return await company_actions.cancel_request(request_id)
    except RequestNotFoundException:
        raise HTTPException(status_code=404, detail="Request not found.")
    except RequestOwnershipException:
        raise HTTPException(status_code=403, detail="This request not your.")








# endpoints from requirements
@router_company_action.delete('/remove/{user_id}', summary="Owner remove User from company", response_model=DeleteFromCompany)
async def remove_user_from_company(
        company_id: int,
        user_id: int = Path(..., title="The ID of user for removing"),
        session: AsyncSession = Depends(get_async_session),
        user: UserId = Depends(get_current_user)  
    ):
    '''Владелец должен иметь возможность исключать пользователей из компании'''
    try:
        company_actions = CompanyActions(session, user)
        return await company_actions.remove_user_from_company(user_id, company_id)
    except CompanyNotFoundException:
        raise HTTPException(status_code=404, detail="Company not found.")
    except NotOwnerCompanyException:
        raise HTTPException(status_code=403, detail="You are not owner if this company.")
    except UserNotFoundException:
        raise HTTPException(status_code=404, detail="User is not a member of the company or user doesnt exist.")



@router_company_action.delete('/leave/{company_id}', summary="User leave company", response_model=LeaveCompany)
async def leave_company(
        company_id: int = Path(..., title="The ID of company"),
        session: AsyncSession = Depends(get_async_session),
        user: UserId = Depends(get_current_user)  
    ):
    '''Пользователь должен иметь возможность выйти из компании'''
    try:
        company_actions = CompanyActions(session, user)
        return await company_actions.leave_company(company_id)
    except CompanyNotFoundException:
        raise HTTPException(status_code=404, detail="Company not found.")
    except UserNotFoundException:
        raise HTTPException(status_code=403, detail="You are not a member of this company.")


@router_company_action.get('/requests/', summary="All user's requests", response_model=List[CompanyActionSchema])
async def user_list_requests(
        page: int = 1,
        session: AsyncSession = Depends(get_async_session),
        user: UserId = Depends(get_current_user)  
    ):
    '''Реализовать ендпоинт с помощью которого каждый User должен 
    иметь возможность посмотреть список своих запросов в компании'''
    company_actions = CompanyActions(session, user)
    return await company_actions.user_list_requests(page)
   

@router_company_action.get('/invitations/', summary="All user's invitations", response_model=List[CompanyActionSchema])
async def user_list_invitations(
        page: int = 1,
        session: AsyncSession = Depends(get_async_session),
        user: UserId = Depends(get_current_user)  
    ):
    '''Реализовать ендпоинт с помощью которого каждый User должен 
    иметь возможность посмотреть список приглашений его в компани'''
    company_actions = CompanyActions(session, user)
    return await company_actions.user_list_invitations(page)

@router_company_action.get('/owner_invite/', summary="All owner's invitations", response_model=List[CompanyActionSchema])
async def owner_list_invitations(
        page: int = 1,
        session: AsyncSession = Depends(get_async_session),
        user: UserId = Depends(get_current_user)  
    ):
    '''Реализовать еднпоинт с помощью которого Владелец 
    компании может увидеть список приглашенных пользователей'''
    company_actions = CompanyActions(session, user)
    return await company_actions.owner_list_invitations(page)

@router_company_action.get('/requests/{company_id}', summary="Requests in company", response_model=List[CompanyActionSchema])
async def requests_in_company(
        page: int = 1,
        company_id: int = Path(..., title="The ID of company"),
        session: AsyncSession = Depends(get_async_session),
        user: UserId = Depends(get_current_user)  
    ):
    '''Реализовать ендпоинт с помощью которого Владелец компании 
    может увидеть список запросов на вступление в компанию'''
    try:
        company_actions = CompanyActions(session, user)
        return await company_actions.requests_in_company(page, company_id)
    except NotOwnerCompanyException:
        raise HTTPException(status_code=403, detail="You are not a owner of this company")

@router_company_action.get('/users/{company_id}', summary="Users in company", response_model=List[CompanyUsers])
async def users_in_company(
        page: int = 1,
        company_id: int = Path(..., title="The ID of company"),
        session: AsyncSession = Depends(get_async_session),
        user: UserId = Depends(get_current_user)  
    ):
    '''Реализовать ендпоинт с помощью которого можно увидеть 
    список пользователей в компании'''
    try:
        company_actions = CompanyActions(session, user)
        return await company_actions.users_in_company(page, company_id)
    except CompanyNotFoundException:
        raise HTTPException(status_code=404, detail="Company not found")