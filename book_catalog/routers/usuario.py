from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from book_catalog.models.usuario import User
from book_catalog.schemas.usuario import UserCreate, UserDeleted, UserPublic, UserUpdate
from book_catalog.utils.database import get_session
from book_catalog.utils.security import get_current_user, get_password_hash

router = APIRouter(prefix='/usuario', tags=['usuario'])
Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post(path='/', response_model=UserPublic, status_code=HTTPStatus.OK)
async def cria_usuario(db: Session, user_in: UserCreate):

    user_db = await db.scalar(select(User).where(
        (User.username == user_in.username) | (User.email == user_in.email))
        )

    if user_db:
        if user_in.username == user_db.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT, detail='Username already created')
        if user_in.email == user_db.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT, detail='Email already created')

    user_db = User(
        username=user_in.username,
        email=user_in.email,
          password=get_password_hash(user_in.password))

    db.add(user_db)
    await db.commit()
    await db.refresh(user_db)

    return user_db


@router.put(path='/{user_id}', response_model=UserPublic, status_code=HTTPStatus.OK)
async def atualiza_usuario(db: Session, user_id: int,
                           user_update: UserUpdate,
                           current_user: CurrentUser):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enought permission'
        )

    user_db = await db.scalar(select(User).where(User.id == user_id))

    try:
        user_db.email = user_update.email
        user_db.username = user_update.username
        user_db.password = get_password_hash(user_update.password)
        await db.commit()
        await db.refresh(user_db)
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='Email or Username already exists')

    return user_db


@router.delete(path='/{user_id}', response_model=UserDeleted, status_code=HTTPStatus.OK)
async def deleta_usuario(db: Session, user_id: int, current_user: CurrentUser):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enought permission'
        )
    user_db = await db.scalar(select(User).where(User.id == user_id))

    await db.delete(user_db)
    await db.commit()

    return {'message': 'Account deleted'}
