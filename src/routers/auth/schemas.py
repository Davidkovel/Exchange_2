import re
from typing import Annotated

from fastapi import HTTPException
from pydantic import BaseModel, constr, Field, field_validator

userEmail = Annotated[constr(min_length=1, max_length=50), Field(
    title="User Email",
    description="E-mail пользователя",
    min_length=1,
    max_length=50,
    examples=['yellowstone1980@gmail.com']
)]

userWalletAdress = Annotated[constr(min_length=100, max_length=100), Field(
    title="Wallet Address",
    description="Адрес кошелька пользователя в сети Ethereum",
    min_length=42,
    max_length=42,
    examples=['0x1234567890abcdef1234567890abcdef12345678']
)]

userPassword = Annotated[constr(min_length=6, max_length=100), Field(
    title="User Password",
    description="""
    Пароль пользователя, к которому предъявляются следующие требования:

    Длина пароля не менее 6 символов.
    Присутствуют латинские символы в нижнем и верхнем регистре.
    Присутствует минимум одна цифра.
    """,
    min_length=6,
    max_length=100,
    examples=['$aba4821FWfew01#.fewA$']
)]


class UserModel(BaseModel):
    """
    Информация о профиле пользователя
    """

    email: userEmail
    password: userPassword

    @field_validator('email', mode='before')
    def validate_email(cls, email):
        if not email:
            raise HTTPException(status_code=400, detail="E-mail не указан.")
        elif not re.search(pattern=r'^[-\w\.]+@([-\w]+\.)+[-\w]{2,4}$', string=email):
            raise HTTPException(status_code=400, detail="E-mail не валидный.")
        elif len(email) > 50:
            raise HTTPException(status_code=400, detail="Длина e-mail превышает допустимый лимит.")

        return email

    @field_validator('password', mode='before')
    def validate_password(cls, password):
        if not password:
            raise HTTPException(status_code=400, detail="Пароль не указан.")
        elif len(password) < 6:
            raise HTTPException(status_code=400, detail="Недостаточно надежный пароль.")
        elif len(password) > 100:
            raise HTTPException(status_code=400, detail="Длина пароля превышает допустимый лимит.")

        return password


class UserResponseModel(BaseModel):
    """
    Информация о профиле пользователя без пароля
    """

    email: userEmail
    wallet_address: userWalletAdress
    user_balance: float


class DepositRequestModel(BaseModel):
    email: userEmail
    wallet_address: userWalletAdress
    amount_user: float


class OAuthForm(BaseModel):
    email: userEmail
    password: userPassword


class Token(BaseModel):
    token: str = Field(
        title="Access Token",
        default="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    )
