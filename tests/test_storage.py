import random

import pytest

from app.storage import create_conn, set_max_offset, get_max_offset


@pytest.mark.asyncio
async def test_max_offset():
    await create_conn()
    value = random.randint(1, 100500)

    await set_max_offset(value)

    assert value == await get_max_offset(-1)
