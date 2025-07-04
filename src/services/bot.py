from aiogram import Bot, Dispatcher, Router, types
from fastapi import Request

from src.data.commands import withdraw_balance_by_user_email
from src.database.db import db_pool

TELEGRAM_BOT_TOKEN = "8060180734:AAHqu98jhPxeS4lEB_NKPHn37Q7ZogUbha8"
TELEGRAM_CHAT_ID = "-1002704025045"

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

approve_invoice_router = Router()


@approve_invoice_router.callback_query(lambda c: c.data.startswith(('approve_', 'reject_')))
async def process_callback(callback_query: types.CallbackQuery):
    action, email, *rest = callback_query.data.split('_')

    if callback_query.data.startswith('approve_'):
        db_session = db_pool()
        usdt_amount = rest[0]

        await withdraw_balance_by_user_email(db_session=db_session, user_email=email,
                                             amount=float(usdt_amount))
    else:
        pass
        # await callback_query.answer("Платеж отклонен")

    await bot.delete_message(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id
    )


async def start_bot():
    dp.include_router(approve_invoice_router)
    await dp.start_polling(bot)
