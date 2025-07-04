from enum import unique

from sqlalchemy import Column, Integer, String, Boolean, Float

from src.database.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, index=True)
    email = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    wallet_address = Column(String(100), nullable=True, unique=True)
    usdt_balance = Column(Float, default=0.0)
    is_google = Column(Boolean, default=False)

