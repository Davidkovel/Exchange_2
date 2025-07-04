from typing import Union

from sqlalchemy import select, or_, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.logger import logger
from src.routers.auth.model import User
from src.routers.auth.schemas import OAuthForm, userEmail, UserModel



async def insert_money_by_user_wallet_address(db_session: AsyncSession, wallet_address: str, amount: float):
    try:
        user_q = select(User).where(User.wallet_address == wallet_address)
        user = (await db_session.execute(user_q)).scalar_one_or_none()

        if not user:
            return False

        stmt = (
            update(User)
            .where(User.wallet_address == wallet_address)
            .values(usdt_balance=User.usdt_balance + amount)
        )
        await db_session.execute(stmt)
        await db_session.commit()
        return True
    except Exception as e:
        logger.error(f"Error inserting money: {e}")
        return False