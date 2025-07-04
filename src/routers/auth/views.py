import os
from typing import Annotated

from authlib.integrations.starlette_client import OAuth

from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer
from starlette.responses import FileResponse

from src.core.resources import templates
from src.data.commands import authenticate_user, get_user_by, add_new_user, insert_address_by_user_email, \
    get_user_by_login
from src.routers.auth.model import User
from src.routers.auth.schemas import OAuthForm, Token, UserModel, UserResponseModel, userWalletAdress
from src.utils.hasher import Hasher
from src.utils.security import create_access_token, decode_access_token
from src.routers.auth.services import WalletAddressService

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter(prefix='/api/auth')

fake_db = {}

oauth = OAuth()

oauth.register(
    name='google',
    client_id="GOOGLE_CLIENT_ID",
    client_secret="GOOGLE_CLIENT_SECRET",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user_by_token(request: Request, token: Annotated[Token, Depends(oauth2_scheme)]) -> User:
    db_session = request.state.db_session

    UnauthorizedResponse = HTTPException(status_code=401, detail="Переданный токен не существует либо некорректен.")

    payload = decode_access_token(token=token)
    if not payload:
        raise UnauthorizedResponse

    user_email= payload.get("sub")
    if not user_email:
        raise UnauthorizedResponse

    user = await get_user_by_login(email=user_email, db_session=db_session)
    if not user:
        raise UnauthorizedResponse

    return user


@router.post("/login")
async def login(request: Request, form_data: UserModel):
    db_session = request.state.db_session

    user = await authenticate_user(form_data=form_data, db_session=db_session)
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь с указанным логином и паролем не найден")

    access_token_expire = None
    access_token = create_access_token(data={"sub": form_data.email}, expire_delta=access_token_expire)

    response = JSONResponse(status_code=200, content=Token(token=access_token).dict())

    return response


@router.get('/me/profile', response_model=UserResponseModel)
async def send_my_profile(user: Annotated[User, Depends(get_current_user_by_token)]):
    amount = round(user.usdt_balance, 2)
    return JSONResponse(status_code=200, content=UserResponseModel(
        email=user.email,
        wallet_address=user.wallet_address if userWalletAdress else None,
        user_balance=amount if amount else 0.0
    ).dict())

@router.post("/register", response_model=UserResponseModel)
async def register_new_user(request: Request, user_data: UserModel):
    db_session = request.state.db_session

    check_user = await get_user_by(db_session, user_data)
    if check_user:
        raise HTTPException(status_code=409,
                            detail="Пользователь с таким e-mail, номером телефона или логином уже зарегистрирован.")

    new_user = await add_new_user(user_data=user_data, db_session=db_session)

    wallet_address_service = await WalletAddressService.generate_wallet_address()
    wallet_address = wallet_address_service['address']
    await insert_address_by_user_email(user_data=user_data, wallet_address=wallet_address, db_session=db_session)

    return JSONResponse(status_code=201,
                        content=UserResponseModel(email=new_user.email, wallet_address=wallet_address).dict())

#
# @router.get("/google-login", response_class=HTMLResponse)
# async def google_login(request: Request):
#     redirect_uri = request.url_for("auth_google")
#     return await oauth.google.authorize_redirect(request, redirect_uri)
#
#
# @router.get("/auth/google")
# async def auth_google(request: Request, token: str):
#     try:
#         db_session = request.state.db_session
#
#         token = await oauth.google.authorize_access_token(request)
#         user_info = await oauth.google.parse_id_token(request, token)
#         email = user_info["email"]
#
#         user = get_user_by(db_session, email)
#         if not user:
#             user = User(email=email, password=None, is_google=True)
#
#             await add_new_user(user_data=user, db_session=db_session)
#
#             jwt_token = create_access_token(data={"sub": user.email})
#
#             return {"access_token": jwt_token}
#     except ValueError:
#         raise HTTPException(status_code=400, detail="Ошибка аутентификации")

# 12345asdf
#
# a1@gmail.com