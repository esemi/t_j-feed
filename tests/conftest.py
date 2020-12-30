import asyncio
from typing import Any

import pytest
from starlette.config import environ
from starlette.testclient import TestClient

from app import webapp

environ['TESTING'] = 'TRUE'


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
def mocked_storage(mocker):
    mocker.patch('aioredis.create_redis_pool', return_value=MockStorage())


@pytest.fixture()
def client():
    with TestClient(webapp) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def mocked_grabber(mocker):
    mocker.patch('app.grabber.fetch_last_comments', return_value=[])
