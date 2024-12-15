import asyncio
import os
import pytest
from prompt_toolkit.shortcuts import yes_no_dialog

from app.config import settings
from app.database import Base, async_session_maker, engine
from app.models import Documents, Documents_text

from fastapi.testclient import TestClient
from httpx import AsyncClient
from app.main import app


@pytest.fixture(scope='session', autouse=True)
async def settings_db():
    assert settings.MODE == 'TEST'

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

        await conn.run_sync(Base.metadata.create_all)

    #
    # async with engine.connect() as conn:
    #     for table in Base.metadata.tables.values():
    #         await conn.execute(table.delete())
    #     await conn.commit()


@pytest.fixture(scope='session')
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# @pytest.fixture()
# def test_file_path():
#     test_file = 'text1.png'
#     return test_file


@pytest.fixture(scope='function')
async def ac():
    async with AsyncClient(app=app, base_url='http://test') as ac:
        yield ac


@pytest.fixture(scope='function')
async def session():
    async with async_session_maker() as session:
        yield session



@pytest.fixture()
def test_file_path():
    test_file = os.path.join(os.path.dirname(__file__), 'text1.png')
    return test_file