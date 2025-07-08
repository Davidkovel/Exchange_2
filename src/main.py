import asyncio
import json
import logging
import time

from contextlib import asynccontextmanager

import aio_pika

import uvicorn
from aiogram import Bot, Dispatcher, Router

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from starlette.middleware.base import RequestResponseEndpoint
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.responses import FileResponse

from src.core.resources import templates
from src.data.commands import withdraw_balance_by_user_email
from src.database.base import Base
from src.data.user_balance_commands import insert_money_by_user_wallet_address
from src.database.db import create_all_tables, db_pool
from src.logger import logger
from src.routers.auth.schemas import DepositRequestModel
from src.routers.auth.views import router as auth_router, login
from src.routers.payment.views import transaction_router

from src.services.bot import start_bot


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(start_bot())
    asyncio.create_task(consume_messages())
    await create_all_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.mount("/src/static", StaticFiles(directory="src/static"), name="static")


@app.middleware("http")
async def db_session_middleware(request: Request, call_next: RequestResponseEndpoint):
    async with db_pool() as db_session:
        request.state.db_session = db_session
        response = await call_next(request)

    return response


async def consume_messages():
    time.sleep(11)
    connection = await aio_pika.connect_robust(
        host="rabbitmq",
        port=5672,
        login="admin",
        password="admin"
    )

    channel = await connection.channel()

    await channel.set_qos(prefetch_count=1)

    queue = await channel.declare_queue("payment_queue", durable=True)

    async def on_message(message: aio_pika.IncomingMessage):
        db_session = db_pool()
        # print(f"Received message: {message.body.decode()}")
        await process_payment(message=message, db_session=db_session)

    print(" [*] Waiting for messages. To exit press CTRL+C")
    await queue.consume(on_message)


async def process_payment(message: aio_pika.IncomingMessage, db_session: AsyncSession):
    async with message.process():
        try:
            data = json.loads(message.body.decode())

            # print(f"Processing payment: {data}")
            user_wallet_address = data['wallet_address']
            user_balance_usdt = round(float(data['user_balance']), 2)

            success = await insert_money_by_user_wallet_address(
                wallet_address=user_wallet_address,
                amount=user_balance_usdt,
                db_session=db_session
            )

        except Exception as e:
            logger.error(f"Error processing message: {e}")


@app.get("/")
async def root(request: Request):
    response = templates.TemplateResponse("index.html", {"request": request})
    response.headers["Cache-Control"] = "public, max-age=300"  # Кеш на 5 минут (300 сек)
    return response


@app.get("/login-page", response_class=HTMLResponse)
async def login_page(request: Request):
    response = templates.TemplateResponse("auth.html", {"request": request})
    response.headers["Cache-Control"] = "public, max-age=300"
    return response


@app.get("/withdraw-page", response_class=HTMLResponse)
async def withdraw_page(request: Request):
    response = templates.TemplateResponse("send_payment_invoice.html", {"request": request})
    response.headers["Cache-Control"] = "public, max-age=300"
    return response


app.include_router(router=auth_router)
app.include_router(router=transaction_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # или конкретный домен вместо "*"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()

# gate торговый пароль 000000

# http://localhost:8000/docs/
