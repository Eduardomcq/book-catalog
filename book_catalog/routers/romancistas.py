from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from book_catalog.models.romancista import Romancista
from book_catalog.models.usuario import User
from book_catalog.schemas.romancista import (
    BaseRomancista,
    RomancistaCreated,
    RomancistaDeleted,
    RomancistaList,
    RomancistaQuery,
)
from book_catalog.utils.database import get_session, sanitiza_texto
from book_catalog.utils.security import get_current_user

router = APIRouter(prefix='/romancista', tags=['romancista'])
Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
QueryStr = Annotated[RomancistaQuery, Query()]


@router.post(path='/', response_model=RomancistaCreated, status_code=HTTPStatus.OK)
async def registra_romancista(
    db: Session, current_user: CurrentUser, romancista_in: BaseRomancista
    ):

    romancista_in.nome = sanitiza_texto(romancista_in.nome)

    romancista_db = await db.scalar(
        select(Romancista).where(
            Romancista.nome == romancista_in.nome
            )
        )

    if romancista_db:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=f'{romancista_db.nome} já consta no MADR'
        )

    romancista_db = Romancista(
        nome=romancista_in.nome
    )

    db.add(romancista_db)
    await db.commit()
    await db.refresh(romancista_db)

    return romancista_db


@router.delete(path='/{id_romancista}', response_model=RomancistaDeleted, status_code=HTTPStatus.OK)
async def deleta_romancista(
    id_romancista: int, current_user: CurrentUser, db: Session
    ):

    romancista_db = await db.scalar(select(Romancista).where(Romancista.id == id_romancista))

    if not romancista_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Romancista não consta no MADR"
        )

    await db.delete(romancista_db)
    await db.commit()

    return {'message': "Romancista deletada no MADR"}


@router.patch(path='/{id_romancista}', response_model=RomancistaCreated, status_code=HTTPStatus.OK)
async def atualiza_romancista(
    id_romancista: int, romancista_in: BaseRomancista, current_user: CurrentUser, db: Session
    ):

    romancista_in.nome = sanitiza_texto(romancista_in.nome)

    romancista_db = await db.scalar(
        select(Romancista).where(Romancista.id == id_romancista)
        )

    if not romancista_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Romancista não consta no MADR"
        )

    try:
        romancista_db.nome = romancista_in.nome
        await db.commit()
        await db.refresh(romancista_db)
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=f'{romancista_in.nome} já consta no MADR'
        )

    return romancista_db


@router.get(path='/{id_romancista}',
            response_model=RomancistaCreated,
            status_code=HTTPStatus.OK)
async def busca_romancista_por_id(
    id_romancista: int, current_user: CurrentUser, db: Session
    ):

    romancista_db = await db.scalar(select(Romancista).where(Romancista.id == id_romancista))

    if not romancista_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Romancista não consta no MADR"
        )

    return romancista_db


@router.get(path='/',
            response_model=RomancistaList,
            status_code=HTTPStatus.OK)
async def query_romancista_por_nome(
    current_user: CurrentUser,
    db: Session,
    filter: QueryStr
):
    query = select(Romancista).filter(Romancista.nome.contains(filter.nome))
    romancista_db = await db.scalars(query.offset(filter.offset).limit(filter.limit))

    return {"romancistas": romancista_db.all()}
