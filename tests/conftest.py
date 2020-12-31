from typing import Any

import pytest
from starlette.testclient import TestClient

from tj_feed.app import webapp
from tj_feed.storage import create_conn


class MockStorage:
    def __init__(self):
        self._data = {}

    async def set(self, key, value):
        self._data[key] = value

    async def get(self, key) -> Any:
        return self._data.get(key)

    def close(self):
        pass

    async def wait_closed(self) -> bool:
        return True


@pytest.fixture(autouse=True)
@pytest.mark.asyncio
async def mocked_storage(mocker):
    mocker.patch('aioredis.create_redis_pool', return_value=MockStorage())
    await create_conn()


@pytest.fixture()
def client():
    with TestClient(webapp) as test_client:
        yield test_client
