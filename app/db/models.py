from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.declarative import declarative_base

DeclarativeBase = declarative_base()

class Base(DeclarativeBase, AsyncAttrs):
    __abstract__ = True
    __tablename__ = "base_table"

    id = Column(Integer, primary_key=True, index=True)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    age = Column(Integer)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    description = Column(String)