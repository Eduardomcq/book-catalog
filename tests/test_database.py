from dataclasses import asdict

import pytest
from sqlalchemy import select

from book_catalog.models.usuario import User
from book_catalog.utils.database import sanitiza_texto


@pytest.mark.asyncio
async def test_database(session, mock_db_time):

    with mock_db_time(model=User) as time:
        user = User(
            username='test',
            email='test@test.com',
            password='test'
        )
        session.add(user)
        await session.commit()

    user = await session.scalar(select(User).where(User.username == 'test'))
    user = asdict(user)

    assert user == {
        'id': 1,
        'username': 'test',
        'email': 'test@test.com',
        'password': 'test',
        'created_at': time,
        'updated_at': time
    }


@pytest.mark.parametrize("texto, expected",
                         [("Machado de Assis", "machado de assis"),
                          ("Manuel        Bandeira", "manuel bandeira"),
                          ("Edgar Alan Poe         ", "edgar alan poe"),
                          ("Androides Sonham Com Ovelhas Elétricas?", "androides sonham com ovelhas elétricas"),
                          ("  breve  história  do tempo ", "breve história do tempo"),
                          ("O mundo assombrado pelos demônios", "o mundo assombrado pelos demônios")])
def test_sanitiza_texto(texto, expected):

    texto_sanitizado = sanitiza_texto(texto)

    assert texto_sanitizado == expected
