from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from book_catalog.models.usuario import User
from book_catalog.schemas.auth import Token
from book_catalog.utils.database import get_session
from book_catalog.utils.security import generate_jwt, validate_password, get_current_user

router = APIRouter(prefix='/auth', tags=['auth'])
Session = Annotated[AsyncSession, Depends(get_session)]
Form = Annotated[OAuth2PasswordRequestForm, Depends()]
CurrentUser = Annotated[User, Depends(get_current_user)]

@router.post(path='/token', response_model=Token, status_code=HTTPStatus.OK)
async def create_token(
    db: Session,
    form_data: Form
):
    user_db = await db.scalar(select(User).where(User.email == form_data.username))

    if not user_db:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                            detail='email or password not found')

    if not validate_password(form_data.password, user_db.password):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                            detail='email or password not found')

    token = generate_jwt(form_data.username)

    return Token(
        access_token=token,
        token_type='bearer'
    )


@router.post(path='/refresh_token',
             status_code=HTTPStatus.OK,
             response_model=Token)
async def refresh_token(
    current_user: CurrentUser
):
    new_access_toke = generate_jwt({'sub':current_user.email})

    return Token(
        access_token=new_access_toke,
        token_type='bearer'
    )
    
