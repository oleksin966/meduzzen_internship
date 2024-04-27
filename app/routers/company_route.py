from fastapi import APIRouter, Depends, HTTPException, status, Security
from db.database import get_async_session
from schemas.user_schema import UserEmail
from schemas.company_schema import CompanySchema, CompanyCreate, CompanyUpdate
from utils.auth import VerifyToken, get_current_user
from utils.utils import get_auth_user
from sqlalchemy.ext.asyncio import AsyncSession
from services.company_service import CompanyServiceCrud
from typing import List

router_company = APIRouter()
auth = VerifyToken()

@router_company.get('/companies', summary="Get all Companies", response_model=List[CompanySchema])
async def get_all_companies(
		page: int,
        session: AsyncSession = Depends(get_async_session),
        email: UserEmail = Depends(get_current_user),
        token: str = Security(auth.verify),
    ):
    user = await get_auth_user(session, email)
    company_service = CompanyServiceCrud(session, user)
    return await company_service.get_all_companies(page)

@router_company.get('/company/{company_id}', summary="Get Company by ID", response_model=CompanySchema)
async def get_company_by_id(
		company_id: int,
        session: AsyncSession = Depends(get_async_session),
        email: UserEmail = Depends(get_current_user),
        token: str = Security(auth.verify),
    ):
    user = await get_auth_user(session, email)
    company_service = CompanyServiceCrud(session, user)
    company = await company_service.get_company_by_id(company_id)
    if company is None:
    	raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company with this ID doesnt exsit"
        )
    return company


@router_company.post('/create_company', summary="Create Company", response_model=CompanySchema)
async def create_company(
        company: CompanySchema = Depends(CompanyCreate),
        session: AsyncSession = Depends(get_async_session),
        email: UserEmail = Depends(get_current_user),
        token: str = Security(auth.verify),
    ):
    user = await get_auth_user(session, email)
    company_service = CompanyServiceCrud(session, user)
    return await company_service.create_company(company)

@router_company.put('/edit_company', summary="Edit info Company", response_model=CompanySchema)
async def update_company(
        company_id: int,
        company_update: CompanyUpdate = Depends(),
        session: AsyncSession = Depends(get_async_session),
        email: UserEmail = Depends(get_current_user),
        token: str = Security(auth.verify),
    ):

    data = company_update.model_dump()
    if data["name"] is None:
        data.pop("name", None)

    if data["description"] is None:
        data.pop("description", None)

    if data["visibility"] is None:
        data.pop("visibility", None)

    user = await get_auth_user(session, email)
    company_service = CompanyServiceCrud(session, user)
    company = await company_service.update_company(company_id, data)
    if company is None:
    	raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company with this ID doesnt exsit"
        )
    return company


@router_company.delete('/delete_company', summary="Delete Company", response_model=CompanySchema)
async def delete_company(
        company_id: int,
        session: AsyncSession = Depends(get_async_session),
        email: UserEmail = Depends(get_current_user),
        token: str = Security(auth.verify),
    ):
    user = await get_auth_user(session, email)
    company_service = CompanyServiceCrud(session, user)
    company = await company_service.delete_company(company_id)
    if company is None:
    	raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company with this ID doesnt exsit"
        )
    return company 
