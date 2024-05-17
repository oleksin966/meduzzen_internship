import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings  
from app.db.database import get_async_session
from app.utils.auth import get_current_user
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator
from app.services.company_service import CompanyActions


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
      yield c

@pytest.fixture(scope="module")
def test_user():
    return {"username": "test", "password": "test"}

@pytest.fixture(scope="module")
def test_company():
    return {"name": "mycom", "description": "myDesc"}