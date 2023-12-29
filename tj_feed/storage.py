"""Storage."""
import datetime
import operator
from dataclasses import asdict
from typing import List

import aioredis

from tj_feed import settings
from tj_feed.grabber.parser import User

db_pool: aioredis.client.Redis = aioredis.from_url(
    settings.REDIS_DSN,
    encoding='utf-8',
    decode_responses=True,
)

TOP_LIST_KEY = 'tinkoff:top'
TOP_UPDATED_AT = 'tinkoff:updated_at'
USER_KEY = 'tinkoff:user:{0}'


async def update_top(users: List[User]) -> None:
    user_ids = set()
    for user in users:
        await db_pool.hset(USER_KEY.format(user.user_id), mapping=asdict(user))
        user_ids.add(user.user_id)

    await db_pool.delete(TOP_LIST_KEY)
    await db_pool.sadd(TOP_LIST_KEY, *user_ids)
    await db_pool.set(TOP_UPDATED_AT, datetime.datetime.utcnow().isoformat())


async def get_updated_at() -> str:
    return (await db_pool.get(TOP_UPDATED_AT)) or ''


async def get_top(limit: int) -> List[User]:
    user_ids = await db_pool.smembers(TOP_LIST_KEY)
    if not user_ids:
        return []

    all_users: List[User] = []
    for user_id in user_ids:
        user_raw = await db_pool.hgetall(
            USER_KEY.format(user_id),
        )
        user = User(
            user_id=int(user_raw['user_id']),
            badges=user_raw['badges'],
            comments_count=int(user_raw['comments_count']),
            image=user_raw['image'] or None,
            karma=int(user_raw['karma']),
            karma_by_comments=int(user_raw['karma_by_comments']),
            name=user_raw['name'],
            ban=user_raw.get('ban', ''),
        )
        all_users.append(user)

    all_users.sort(key=operator.attrgetter('karma'), reverse=True)
    return all_users[:limit]
