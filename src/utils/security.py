from datetime import timedelta, datetime
from typing import Optional

import jwt

from src.logger import logger


# from app.config.config import Config
# from src.routers.auth.schemas import Token


def create_access_token(data: dict, expire_delta: Optional[timedelta] = None):
    to_encode = data.copy()

    if expire_delta:
        expire = datetime.utcnow() + expire_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)

    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(payload=to_encode, key="secret_key", algorithm="HS256")

    return encode_jwt


def decode_access_token(token):
    try:
        payload = jwt.decode(jwt=token, key="secret_key", algorithms="HS256")

        return payload
    except Exception as e:
        logger.error(e)
        return None
