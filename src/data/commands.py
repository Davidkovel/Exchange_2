from typing import Union

from sqlalchemy import select, or_, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.routers.auth.schemas import OAuthForm, userEmail, UserModel
from src.routers.payment.model import WithdrawTransaction
from src.utils.hasher import Hasher
from src.routers.auth.model import User


async def insert_address_by_user_email(db_session: AsyncSession, user_data: UserModel, wallet_address: str):
    stmt = (
        update(User)
        .where(User.email == user_data.email)
        .values(wallet_address=wallet_address)
    )

    await db_session.execute(stmt)
    await db_session.commit()


async def get_user_by(db_session: AsyncSession, user_data: UserModel):
    query = select(User).where(
        or_(User.email == user_data.email)
    )

    result = await db_session.execute(query)
    user = result.scalars().all()

    return user


async def get_user_by_login(email: userEmail, db_session: AsyncSession) -> Union[User, bool]:
    if not email:
        return None

    query = select(User).where(User.email == email)
    result = await db_session.execute(query)
    user = result.scalars().one_or_none()

    return user


async def add_new_user(db_session: AsyncSession, user_data: UserModel):
    user_data.password = Hasher.get_password_hash(password=user_data.password)

    new_user = User(
        email=user_data.email,
        password=user_data.password,
    )

    db_session.add(new_user)
    await db_session.commit()

    return new_user


async def authenticate_user(db_session: AsyncSession, form_data: UserModel) -> Union[User, bool]:
    user = await get_user_by_login(email=form_data.email, db_session=db_session)

    if not user:
        return False
    if not Hasher.verify_password(plain_password=form_data.password, hashed_password=user.password):
        return False

    return user


# Transactions

async def get_user_balance_by_user_email(db_session: AsyncSession, user_email: userEmail) -> float:
    query = select(User.usdt_balance).where(User.email == user_email)

    result = await db_session.execute(query)
    user_balance = result.scalar_one_or_none()
    return user_balance if user_balance is not None else 0.0


async def withdraw_balance_by_user_email(db_session: AsyncSession, user_email: userEmail, amount: float):
    stmt = (
        update(User).where(User.email == user_email)
        .values(usdt_balance=User.usdt_balance - amount)
    )

    await db_session.execute(stmt)
    await db_session.commit()


async def get_withdraw_count(db_session: AsyncSession, user_email: str) -> int:
    stmt = (
        select(WithdrawTransaction).filter(WithdrawTransaction.user_email == user_email).count()
    )

    result = await db_session.execute(stmt)
    return result
