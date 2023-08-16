import asyncio

import pytest
from httpx import AsyncClient

from tj_feed.app import webapp


@pytest.fixture()
async def app_client() -> AsyncClient:
    """
    Make a 'client' fixture available to test cases.
    """
    async with AsyncClient(app=webapp, base_url="http://test") as test_client:
        yield test_client

@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()
