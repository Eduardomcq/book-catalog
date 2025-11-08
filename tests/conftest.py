
from contextlib import contextmanager
from datetime import datetime

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from book_catalog.app import app
from book_catalog.models.base import table_registry
from book_catalog.models.romancista import Romancista
from book_catalog.models.usuario import User
from book_catalog.utils.database import get_session
from book_catalog.utils.security import get_password_hash


@contextmanager
def _mock_db_time(model, time=datetime(2025, 10, 10)):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_hook)

    yield time

    event.remove(model, 'before_insert', fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope='session')
def create_engine():
    with PostgresContainer('postgres:16', driver='psycopg') as postgres:
        engine = create_async_engine(postgres.get_connection_url())
        yield engine


@pytest_asyncio.fixture
async def session(create_engine):
    async with create_engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(create_engine, expire_on_commit=False) as session:
        yield session

    async with create_engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest_asyncio.fixture
async def add_user_bob(session):

    password = 'bob'
    hashed_password = get_password_hash(password)

    user = User(username='bob',
                email='bob@example.com',
                password=hashed_password)
    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password

    return user


@pytest_asyncio.fixture
async def add_user_mark(session):
    password = 'mark'
    hashed_password = get_password_hash(password)
    user = User(username='mark',
                email='mark@example.com',
                password=hashed_password)
    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password
    return user


@pytest_asyncio.fixture
async def get_token(client, add_user_bob):
    response = client.post(url='/auth/token',
                data={'username': add_user_bob.email,
                        'password': add_user_bob.clean_password})

    return response.json()['access_token']


@pytest_asyncio.fixture
async def add_romancista_patrick(session):
    romancista = Romancista(
        nome='patrick'
    )
    session.add(romancista)
    await session.commit()
    await session.refresh(romancista)

    return romancista


@pytest_asyncio.fixture
async def add_romancista_dan(session):
    romancista = Romancista(
        nome='dan'
    )
    session.add(romancista)
    await session.commit()
    await session.refresh(romancista)

    return romancista
