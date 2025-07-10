from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from src.database.base import Base


class WithdrawTransaction(Base):
    __tablename__ = "withdraw_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    trx_wallet = Column(String, nullable=False)
    usdt_amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", foreign_keys=[user_id])
