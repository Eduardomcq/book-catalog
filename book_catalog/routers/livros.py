from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from book_catalog.models.livro import Livro
from book_catalog.models.romancista import Romancista
from book_catalog.models.usuario import User
from book_catalog.schemas.livro import (
    BookBase,
    BookCreated,
    BookDeleted,
    BookList,
    BookPatch,
    LivroQuery,
)
from book_catalog.utils.database import get_session, sanitiza_texto
from book_catalog.utils.security import get_current_user

router = APIRouter(prefix='/livro', tags=['livro'])

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
QueryStr = Annotated[LivroQuery, Query()]


@router.post(path='/', status_code=HTTPStatus.OK, response_model=BookCreated)
async def registra_livro(
    db: Session,
    current_user: CurrentUser,
    livro_in: BookBase
):

    livro_in.titulo = sanitiza_texto(livro_in.titulo)

    livro_db = await db.scalar(select(Livro).where(Livro.titulo == livro_in.titulo))
    romancista_db = await db.scalar(select(Romancista).where(Romancista.id == livro_in.romancista_id))

    if livro_db:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=f"{livro_db.titulo} já consta no MADR"
        )

    if not romancista_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Romancista não cadastrado"
        )

    livro_db = Livro(
        ano=livro_in.ano,
        titulo=livro_in.titulo,
        romancista_id=livro_in.romancista_id
    )

    db.add(livro_db)
    await db.commit()
    await db.refresh(livro_db)

    return livro_db


@router.delete(path='/{livro_id}', status_code=HTTPStatus.OK, response_model=BookDeleted)
async def deleta_livro(
    db: Session,
    current_user: CurrentUser,
    livro_id: int,
):
    livro_db = await db.scalar(select(Livro).where(Livro.id == livro_id))

    if not livro_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Livro não consta no MADR"
        )

    await db.delete(livro_db)
    await db.commit()

    return {"message": "Livro deletado no MADR"}


@router.patch(path='/{livro_id}', status_code=HTTPStatus.OK, response_model=BookCreated)
async def atualiza_livro(
    db: Session,
    current_user: CurrentUser,
    livro_in: BookPatch,
    livro_id: int
):
    livro_db = await db.scalar(select(Livro).where(Livro.id == livro_id))

    if not livro_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Livro não consta no MADR"
        )

    livro_db.ano = livro_in.ano

    await db.commit()
    await db.refresh(livro_db)

    return livro_db


@router.get('/{livro_id}', status_code=HTTPStatus.OK, response_model=BookCreated)
async def get_livro_by_id(
    db: Session,
    current_user: CurrentUser,
    livro_id: int
):
    livro_db = await db.scalar(select(Livro).where(Livro.id == livro_id))

    if not livro_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Livro não consta no MADR"
        )

    return livro_db


@router.get('/', status_code=HTTPStatus.OK, response_model=BookList)
async def get_livro_by_nome_data(
    current_user: CurrentUser,
    db: Session,
    filter: QueryStr
):
    if filter.titulo is None and filter.ano is None:
        return {
    "livros": []
}
    if filter.titulo:
        query = select(Livro).filter(Livro.titulo.contains(filter.titulo))

    if filter.ano:
        query = select(Livro).where(Livro.ano == filter.ano)

    livro_db = await db.scalars(query)

    return {
    "livros": livro_db.all()
}
