from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, decode, encode, ExpiredSignatureError
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from book_catalog.models.usuario import User
from book_catalog.utils.database import get_session
from book_catalog.utils.settings import Settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')
pwd_context = PasswordHash.recommended()

Session = Annotated[AsyncSession, Depends(get_session)]
Token = Annotated[OAuth2PasswordBearer, Depends(oauth2_scheme)]


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def validate_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def generate_jwt(username: str) -> str:
    payload = {"sub": username}
    payload['exp'] = (datetime.now(ZoneInfo('UTC'))
                      + timedelta(minutes=Settings().ACCESS_TOKEN_EXPIRE_MINUTES))
    token = encode(payload=payload, key=Settings().SECRET_KEY, algorithm=Settings().ALGORITH)

    return token


async def get_current_user(
        session: Session,
        token: Token
):
    auth_erro = HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    try:
        payload = decode(jwt=token, key=Settings().SECRET_KEY, algorithms=Settings().ALGORITH)
        subject_email = payload['sub']

        if not subject_email:
            raise auth_erro

    except DecodeError:
        raise auth_erro
    except ExpiredSignatureError:
        raise auth_erro

    user_db = await session.scalar(select(User).where(User.email == subject_email))

    if not user_db:
        raise auth_erro

    return user_db
