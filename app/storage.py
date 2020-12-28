from typing import Optional

import aioredis

_REDIS_POOL: Optional[aioredis.Redis] = None

KEYS_NS = 't_j_feed'

MAX_OFFSET_KEY = f'{KEYS_NS}:max_offset'
REDIS_HOST = 'redis://127.0.0.1'


async def create_conn():
    global _REDIS_POOL
    _REDIS_POOL = await aioredis.create_redis_pool(REDIS_HOST, minsize=5, maxsize=10)


async def get_max_offset(default: Optional[int]) -> int:
    offset = await _REDIS_POOL.get(MAX_OFFSET_KEY)
    return default if not offset else int(offset)


async def set_max_offset(value: int):
    await _REDIS_POOL.set(MAX_OFFSET_KEY, value)


async def close_conn():
    global _REDIS_POOL
    if _REDIS_POOL:
        _REDIS_POOL.close()
        await _REDIS_POOL.wait_closed()
