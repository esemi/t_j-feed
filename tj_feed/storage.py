from typing import Optional

import aioredis

_REDIS_POOL: Optional[aioredis.Redis] = None

KEYS_NS = 't_j_feed'

MAX_OFFSET_KEY = f'{KEYS_NS}:max_offset'
REDIS_HOST = 'redis://127.0.0.1'


async def create_conn():
    global _REDIS_POOL
    _REDIS_POOL = await aioredis.create_redis_pool(REDIS_HOST, minsize=5, maxsize=10)  # noqa: WPS122, WPS442


async def close_conn():
    global _REDIS_POOL
    if _REDIS_POOL:
        _REDIS_POOL.close()
        await _REDIS_POOL.wait_closed()


def get_connection() -> aioredis.Redis:
    if _REDIS_POOL:
        return _REDIS_POOL
    raise RuntimeError('Redis connection down')


async def get_max_offset(default: int) -> int:
    offset = await get_connection().get(MAX_OFFSET_KEY)
    if offset:
        return int(offset)
    return default


async def set_max_offset(new_value: int):
    await get_connection().set(MAX_OFFSET_KEY, new_value)
