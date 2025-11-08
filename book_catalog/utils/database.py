import re
import string

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from book_catalog.utils.settings import Settings

engine = create_async_engine(Settings().DATABASE_URL)


async def get_session():
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session


def sanitiza_texto(texto: str):

    traducao = str.maketrans('', '', string.punctuation)
    texto = texto.translate(traducao)

    texto = texto.lower().strip()

    texto = re.sub(r"\s+", " ", texto)

    return texto
