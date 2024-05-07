from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.declarative import declarative_base

DeclarativeBase = declarative_base()

class Base(DeclarativeBase, AsyncAttrs):
    __abstract__ = True
    __tablename__ = "base_table"

    id = Column(Integer, primary_key=True)

class User(Base):
    __tablename__ = "users"

    username = Column(String, unique=True, index=True, nullable=False)
    age = Column(Integer)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    description = Column(String)
    disabled = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    owned_companies = relationship("Company", back_populates="owner")
    company_users = relationship("CompanyUser", back_populates="user")  



class Company(Base):
    __tablename__ = "companies"

    name = Column(String, nullable=False)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    visibility = Column(Boolean, default=True)


    owner = relationship("User", back_populates="owned_companies")
    company_users = relationship("CompanyUser", back_populates="company")  # Updated line


class Invitation(Base):
    __tablename__ = "invitations"

    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    company = relationship("Company", backref="invitations")
    user = relationship("User", foreign_keys=[user_id], backref="invitations")

class Request(Base):
    __tablename__ = "requests"

    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    company = relationship("Company", backref="requests")
    user = relationship("User", foreign_keys=[user_id], backref="requests")


class CompanyUser(Base):
    __tablename__ = "company_users"

    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    company = relationship("Company", back_populates="company_users")
    user = relationship("User", back_populates="company_users")


