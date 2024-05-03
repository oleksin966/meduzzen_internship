from fastapi import APIRouter, Depends, HTTPException, status, Security, Path
from db.database import get_async_session
from schemas.user_schema import UserEmail, UserId
from schemas.company_schema import CompanySchema, CompanyCreate, CompanyUpdate
from utils.auth import get_current_user
from utils.utils import get_auth_user
from sqlalchemy.ext.asyncio import AsyncSession
from services.company_service import CompanyServiceCrud
from typing import List

router_company = APIRouter(prefix="/company")

@router_company.get('/all', summary="Get all Companies", response_model=List[CompanySchema])
async def get_all_companies(
		page: int = 1,
        session: AsyncSession = Depends(get_async_session),
        user: UserId = Depends(get_current_user),
    ):
    company_service = CompanyServiceCrud(session, user)
    return await company_service.get_all_companies(page)

@router_company.get('/{company_id}', summary="Get Company by ID", response_model=CompanySchema)
async def get_company_by_id(
		company_id: int = Path(..., title="Get company by ID"),
        session: AsyncSession = Depends(get_async_session),
        user: UserId = Depends(get_current_user),
    ):
    company_service = CompanyServiceCrud(session, user)
    company = await company_service.get_company_by_id(company_id)
    if company is None:
    	raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company with this ID doesnt exsit"
        )
    return company


@router_company.post('/create', summary="Create Company", response_model=CompanySchema)
async def create_company(
        company: CompanyCreate,
        session: AsyncSession = Depends(get_async_session),
        user: UserId = Depends(get_current_user),
    ):
    company_service = CompanyServiceCrud(session, user)
    return await company_service.create_company(company)

@router_company.put('/edit/{company_id}', summary="Edit info Company", response_model=CompanySchema)
async def update_company(
        company_update: CompanyUpdate,
        company_id: int = Path(..., title="The ID of the company to update"),
        session: AsyncSession = Depends(get_async_session),
        user: UserId = Depends(get_current_user),
    ):

    data = company_update.dict(exclude_none=True)
    company_service = CompanyServiceCrud(session, user)
    company = await company_service.update_company(company_id, data)
    if company is None:
    	raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company with this ID doesnt exsit"
        )
    return company


@router_company.delete('/delete/{company_id}', summary="Delete Company", response_model=CompanySchema)
async def delete_company(
        company_id: int = Path(..., title="The ID of the company to delete"),
        session: AsyncSession = Depends(get_async_session),
        user: UserId = Depends(get_current_user),
    ):
    company_service = CompanyServiceCrud(session, user)
    company = await company_service.delete_company(company_id)
    if company is None:
    	raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company with this ID doesnt exsit"
        )
    return company 
