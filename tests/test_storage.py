import random

import pytest

from app.storage import set_max_offset, get_max_offset


class MockStorage:
    def __init__(self):
        self._data = {}

    async def set(self, key, value):
        self._data[key] = value

    async def get(self, key):
        return self._data.get(key)


@pytest.mark.asyncio
async def test_max_offset(mocker):
    value = random.randint(1, 100500)

    mocker.patch('app.storage._REDIS_POOL', MockStorage())

    await set_max_offset(value)

    assert value == await get_max_offset(-1)
