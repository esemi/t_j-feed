import asyncio
import logging
import operator
from collections import OrderedDict
from itertools import chain
from typing import Iterable, List, Dict, Union

import aiohttp

from tj_feed.grabber.parser import User, parse_user

CONNECTIONS_LIMIT = 5
CONNECTIONS_TIMEOUT = 30
CONNECTIONS_DNS_CACHE = 300

API_HOST = 'https://social.journal.tinkoff.ru'

API_ENDPOINT_USERS = '/api/v25/profiles/'
API_USERS_PER_PAGE = 100
API_USERS_PARAMS: Dict[str, Union[str, int]] = OrderedDict({
    'order_by': 'karma',
    'unsafe': 'true',
})


async def fetch_top_users(total_limit: int) -> List[User]:
    offsets = list(
        range(0, total_limit, API_USERS_PER_PAGE),
    )
    parsed_users = []
    for offsets_for_processing in chunk(offsets, CONNECTIONS_LIMIT):
        tasks: List[asyncio.Task] = [
            asyncio.create_task(_fetch_users_page(API_USERS_PER_PAGE, offset))
            for offset in offsets_for_processing
        ]
        parsed_users.append(chain.from_iterable(await asyncio.gather(*tasks)))
        del tasks

    all_users: List[User] = list(chain.from_iterable(parsed_users))
    all_users.sort(key=operator.attrgetter('karma'), reverse=True)
    return all_users[:total_limit]


async def _fetch_users_page(limit: int, offset: int) -> Iterable[User]:
    request_params = API_USERS_PARAMS.copy()
    request_params['limit'] = limit
    request_params['offset'] = offset
    resp = await _request(API_ENDPOINT_USERS, request_params)
    return map(parse_user, resp.get('data', []))


async def _request(endpoint: str, request_params: dict) -> dict:
    """Request to unofficial API."""
    timeout = aiohttp.ClientTimeout(total=CONNECTIONS_TIMEOUT)
    conn = aiohttp.TCPConnector(ttl_dns_cache=CONNECTIONS_DNS_CACHE)
    async with aiohttp.ClientSession(timeout=timeout, connector=conn) as session:
        async with session.get(f'{API_HOST}{endpoint}', params=request_params) as resp:
            logging.info(f'fetch comments req_par={request_params} with code={resp.status}')
            resp.raise_for_status()
            return await resp.json()


def chunk(chunk_source: List, size: int) -> List:
    return [
        chunk_source[index: index + size]
        for index in range(0, len(chunk_source), size)
    ]
