import asyncio
import logging
import operator
from asyncio import Semaphore
from itertools import chain
from typing import Iterable, Iterator, List, Optional, Tuple

import aiohttp

from tj_feed import storage
from tj_feed.grabber.parser import Comment, parse_comment, User, parse_user

CONNECTIONS_POOL = Semaphore(5)
CONNECTIONS_TIMEOUT = 30
CONNECTIONS_DNS_CACHE = 300

API_HOST = 'https://social.journal.tinkoff.ru'

API_ENDPOINT_USERS = '/api/v13/profiles/'
API_USERS_PER_PAGE = 100
API_USERS_PARAMS = {
    'order_by': 'karma',
    'unsafe': 'true',
}

API_ENDPOINT_COMMENTS = '/api/v13/comments/'
API_COMMENTS_PER_PAGE = 2000
API_COMMENTS_PARAMS = {
    'include': 'article_path,article_title,user',
    'order_by': 'date_added',
    'unsafe': 'true',
}


def combine_batches_back(total_limit: int, max_offset: int) -> Iterator[Tuple]:
    offset_start = max(0, max_offset - total_limit)
    yield from (
        (local_offset, API_COMMENTS_PER_PAGE)
        for local_offset in range(offset_start, max(max_offset, API_COMMENTS_PER_PAGE), API_COMMENTS_PER_PAGE)
    )


async def fetch_top_users(total_limit: int) -> List[User]:
    tasks = [
        fetch_users_page(API_USERS_PER_PAGE, local_offset, CONNECTIONS_POOL)
        for local_offset in range(0, total_limit, API_USERS_PER_PAGE)
    ]
    tasks = list(map(asyncio.create_task, tasks))

    all_users = list(chain.from_iterable(await asyncio.gather(*tasks)))
    all_users.sort(key=operator.attrgetter('karma'), reverse=True)
    return all_users[:total_limit]


async def fetch_users_page(limit: int, offset: int, lock: Semaphore) -> Iterable[User]:
    params = API_USERS_PARAMS.copy()
    params['limit'] = limit
    params['offset'] = offset
    resp = await _request(API_ENDPOINT_USERS, params, lock)
    return map(parse_user, resp.get('data', []))


async def fetch_last_comments(total_limit: int, max_available_offset: int) -> List[Comment]:
    tasks = [
        fetch_comments_page(local_limit, local_offset, CONNECTIONS_POOL)
        for local_offset, local_limit in combine_batches_back(total_limit, max_available_offset)
    ]
    tasks = list(map(asyncio.create_task, tasks))

    all_comments = list(chain.from_iterable(await asyncio.gather(*tasks)))
    all_comments.sort(key=operator.attrgetter('comment_date'), reverse=True)
    return all_comments[:total_limit]


async def fetch_comments_page(limit: int, offset: int, lock: Semaphore) -> Iterable[Comment]:
    params = API_COMMENTS_PARAMS.copy()
    params['limit'] = limit
    params['offset'] = offset
    resp = await _request(API_ENDPOINT_COMMENTS, params, lock)
    return map(parse_comment, resp.get('data', []))


async def _request(endpoint: str, params: dict, lock: Semaphore) -> dict:
    """Request to unofficial API.
    """

    timeout = aiohttp.ClientTimeout(total=CONNECTIONS_TIMEOUT)
    conn = aiohttp.TCPConnector(ttl_dns_cache=CONNECTIONS_DNS_CACHE)
    async with lock:
        async with aiohttp.ClientSession(timeout=timeout, connector=conn) as session:
            async with session.get(f'{API_HOST}{endpoint}', params=params) as resp:
                logging.info(f'fetch comments req_par={params} with code={resp.status}')
                resp.raise_for_status()
                return await resp.json()


async def search_actual_offset(max_available_offset: int) -> int:
    local_start = max_available_offset

    while True:
        new_max = await search_local_max_offset(local_start)
        if new_max <= local_start:
            break

        local_start = new_max
        await storage.set_max_offset(local_start)

    return local_start


def combine_batches_forward(start_offset: int) -> Iterator[Tuple[int, int]]:
    factors = [0, 1, 3, 5, 8, 13, 21, 34, 55]
    yield from (
        (start_offset + API_COMMENTS_PER_PAGE * factor, 1 if num else API_COMMENTS_PER_PAGE)
        for num, factor in enumerate(factors)
    )


async def fetch_comments_page_next_offset(limit: int, offset: int, lock: Semaphore) -> Optional[int]:
    params = API_COMMENTS_PARAMS.copy()
    params['limit'] = limit
    params['offset'] = offset

    comments: list = (await _request(API_ENDPOINT_COMMENTS, params, lock)).get('data', [])
    if comments:
        return offset + len(comments)
    return 0


async def search_local_max_offset(start_offset: int) -> int:
    tasks = [
        fetch_comments_page_next_offset(local_limit, local_offset, CONNECTIONS_POOL)
        for local_offset, local_limit in combine_batches_forward(start_offset)
    ]
    tasks = list(map(asyncio.create_task, tasks))
    offsets = await asyncio.gather(*tasks)
    return max(offsets)
