from typing import Annotated

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from fastapi.params import Depends

from src.data.commands import get_user_balance_by_user_email, withdraw_balance_by_user_email, get_withdraw_count, \
    create_withdraw_transaction
from src.routers.auth.model import User
from src.routers.auth.views import get_current_user_by_token
from src.routers.payment.schemas import WithdrawRequestModel

from src.services.bot import TELEGRAM_CHAT_ID, bot as tg_bot

transaction_router = APIRouter(prefix="/api/transactions")


@transaction_router.post("/send")
async def send_transaction(request: Request, background_tasks: BackgroundTasks, transaction_data: WithdrawRequestModel,
                           user: Annotated[User, Depends(get_current_user_by_token)]):
    db_session = request.state.db_session

    user_balance = await get_user_balance_by_user_email(db_session=db_session, user_email=user.email)

    if user_balance < transaction_data.usdt_amount:
        raise HTTPException(
            status_code=400,
            detail="Недостаточно средств на балансе"
        )

    withdraw_count = await get_withdraw_count(db_session=db_session, user_id=user.id)

    if withdraw_count >= 1:
        raise HTTPException(status_code=400, detail="Сиз олдин чиқариш қилгансиз. Иккинчи марта чиқариш мумкин эмас.")

    await create_withdraw_transaction(
        db_session=db_session,
        user_id=user.id,
        user_email=user.email,
        trx_wallet=transaction_data.trx_wallet,
        usdt_amount=transaction_data.usdt_amount
    )

    background_tasks.add_task(
        process_payment_invoice,
        email=user.email,
        usdt_amount=transaction_data.usdt_amount,
        trx_wallet=transaction_data.trx_wallet
    )

    return {"status_code": 200, "message": "Transaction sent successfully."}


async def process_payment_invoice(email: str, usdt_amount: float, trx_wallet: str):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить",
                              callback_data=f"approve_{email}_{usdt_amount}_{trx_wallet}")],
        [InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{email}")]
    ])

    message = (
        "🔄 <b>Запрос на вывод средств</b>\n\n"
        f"👤 <b>Пользователь:</b> {email}\n"
        f"💵 <b>Сумма:</b> {usdt_amount} USDT\n"
        f"📨 <b>На кошелек:</b> <code>{trx_wallet}</code>\n\n"
        "Подтвердите или отклоните запрос:"
    )

    await tg_bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, reply_markup=keyboard, parse_mode="HTML")
