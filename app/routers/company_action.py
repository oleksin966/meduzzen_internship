from fastapi import APIRouter, Depends, HTTPException, status, Security, Path
from db.database import get_async_session
from schemas.user_schema import UserEmail, UserId
from schemas.company_schema import CompanySchema, CompanyCreate, CompanyUpdate
from utils.auth import get_current_user
from utils.utils import get_auth_user
from sqlalchemy.ext.asyncio import AsyncSession
from services.company_service import CompanyActions
from typing import List

router_company_action = APIRouter(prefix="/action")

@router_company_action.post('/invite/{user_id}', summary="Owner invite User to company", response_model=None)
async def send_invitation_to_user(
		company_id: int,
		user_id: int = Path(..., title="The ID of User"),
        session: AsyncSession = Depends(get_async_session),
        user: UserId = Depends(get_current_user)
        
    ):
    company_actions = CompanyActions(session, user)
    return await company_actions.send_invitation_to_user(user_id, company_id)

@router_company_action.delete('/cancel_invite/{invitation_id}', summary="Owner cancel invite User to company", response_model=None)
async def cancel_invitation(
		invitation_id: int = Path(..., title="The ID of cancel invitation"),
        session: AsyncSession = Depends(get_async_session),
        user: UserId = Depends(get_current_user)   
    ):
    company_actions = CompanyActions(session, user)
    return await company_actions.cancel_invitation(invitation_id)


@router_company_action.post('/request/{company_id}', summary="User send request to company", response_model=None)
async def send_request(
		company_id: int = Path(..., title="The ID of requested company"),
        session: AsyncSession = Depends(get_async_session),
        user: UserId = Depends(get_current_user)   
    ):
    company_actions = CompanyActions(session, user)
    return await company_actions.send_request(company_id)


@router_company_action.delete('/cancel_request/{request_id}', summary="User cancel request to company", response_model=None)
async def cancel_sent_request(
		request_id: int = Path(..., title="The ID of cancel request to company"),
        session: AsyncSession = Depends(get_async_session),
        user: UserId = Depends(get_current_user)   
    ):
    company_actions = CompanyActions(session, user)
    return await company_actions.cancel_sent_request(request_id)

@router_company_action.post('/accept_request/{request_id}', summary="Owner accept request from User", response_model=None)
async def accept_request_from_user(
		request_id: int = Path(..., title="The ID of accept request to company"),
        session: AsyncSession = Depends(get_async_session),
        user: UserId = Depends(get_current_user)   
    ):
    company_actions = CompanyActions(session, user)
    return await company_actions.accept_request_from_user(request_id)

@router_company_action.delete('/decline_request/{request_id}', summary="Owner decline request from User", response_model=None)
async def decline_request_from_user(
		request_id: int = Path(..., title="The ID of cancel request to company"),
        session: AsyncSession = Depends(get_async_session),
        user: UserId = Depends(get_current_user)   
    ):
    company_actions = CompanyActions(session, user)
    return await company_actions.decline_request_from_user(request_id)

@router_company_action.post('/accept_invite/{invitation_id}', summary="User accept invitation from Owner", response_model=None)
async def accept_invite_from_owner(
		invitation_id: int = Path(..., title="The ID of accepted invitation"),
        session: AsyncSession = Depends(get_async_session),
        user: UserId = Depends(get_current_user)   
    ):
    company_actions = CompanyActions(session, user)
    return await company_actions.accept_invite_from_owner(invitation_id)

@router_company_action.delete('/decline_invite/{invitation_id}', summary="User decline invitation from Owner", response_model=None)
async def decline_invitation(
        invitation_id: int = Path(..., title="The ID of declined invitation"),
        session: AsyncSession = Depends(get_async_session),
        user: UserId = Depends(get_current_user)  
    ):
    company_actions = CompanyActions(session, user)
    return await company_actions.decline_invitation(invitation_id)

@router_company_action.delete('/remove/{user_id}', summary="Owner remove User from company", response_model=None)
async def remove_user_from_company(
        company_id: int,
        user_id: int = Path(..., title="The ID of user for removing"),
        session: AsyncSession = Depends(get_async_session),
        user: UserId = Depends(get_current_user)  
    ):
    company_actions = CompanyActions(session, user)
    return await company_actions.remove_user_from_company(user_id, company_id)

@router_company_action.delete('/leave/{company_id}', summary="User leave company", response_model=None)
async def leave_company(
        company_id: int = Path(..., title="The ID of company"),
        session: AsyncSession = Depends(get_async_session),
        user: UserId = Depends(get_current_user)  
    ):
    company_actions = CompanyActions(session, user)
    return await company_actions.leave_company(company_id)

# @router_company_action.delete('/accept/{user_id}', summary="Cancel invite User to company", response_model=None)
# async def accept_request_from_user(

# 		user_id: int = Path(..., title="The ID of accepted User"),
#         session: AsyncSession = Depends(get_async_session),
#         user: UserId = Depends(get_current_user)   
#     ):
#     company_actions = CompanyActions(session, user)
#     return await company_actions.accept_request_from_user(invitation_id)