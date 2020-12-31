import asyncio
import logging
import operator
import unicodedata
from asyncio import Semaphore
from dataclasses import dataclass
from itertools import chain
from typing import Iterable, Iterator, List, Optional, Tuple

import aiohttp
from typed_json_dataclass import TypedJsonMixin

from tj_feed import storage

HOST = 'https://journal.tinkoff.ru'
API_HOST = 'https://social.journal.tinkoff.ru'
API_ENDPOINT_COMMENTS = '/api/v13/comments/'

DEFAULT_AVATAR = 'https://static2.tinkoffjournal.ru/mercury-front/fbfb8fb7b8ce70bf9516d9028e231419853c5444/face-08.982a.png'

CONNECTIONS_POOL = Semaphore(5)
CONNECTIONS_TIMEOUT = 20
CONNECTIONS_DNS_CACHE = 300

API_COMMENTS_PER_PAGE = 2000


@dataclass
class Comment(TypedJsonMixin):
    user_id: int
    user_name: str
    user_image: Optional[str]

    comment_id: int
    comment_content: str
    comment_date: str
    comment_rating: int

    article_path: str
    article_title: str

    @property
    def comment_link(self) -> str:
        return f'{HOST}{self.article_path}#c{str(self.comment_id)}'

    @property
    def user_link(self) -> str:
        return f'{HOST}/user{str(self.user_id)}/'


def unicode_normalize(source: str) -> str:
    try:
        source = source.replace('\xa0', ' ')
    except AttributeError:
        return ''

    filtered_chars = filter(lambda char: unicodedata.category(char)[0] != 'C', source)
    return ''.join(filtered_chars)


def parse_comment(comment: dict) -> Comment:
    user: dict = comment.get('author', {})
    rating: dict = comment.get('rating', {})
    return Comment(
        user_id=int(user.get('id')),
        user_name=unicode_normalize(user.get('name')),
        user_image=user.get('image') if user.get('image') else DEFAULT_AVATAR,
        comment_id=int(comment.get('id')),
        comment_content=unicode_normalize(comment.get('text')),
        comment_date=comment.get('date_added'),
        comment_rating=rating.get('likes', 0) - rating.get('dislikes', 0),
        article_title=unicode_normalize(comment.get('article_title')),
        article_path=comment.get('article_path'),
    )


def combine_batches_back(total_limit: int, max_offset: int) -> Iterator[Tuple]:
    offset_start = max(0, max_offset - total_limit)
    yield from (
        (local_offset, API_COMMENTS_PER_PAGE)
        for local_offset in range(offset_start, max(max_offset, API_COMMENTS_PER_PAGE), API_COMMENTS_PER_PAGE)
    )


async def fetch_last_comments(total_limit: int, max_available_offset: int) -> List[Comment]:
    tasks = [
        fetch_comments_page(local_limit, local_offset, CONNECTIONS_POOL)
        for local_offset, local_limit in combine_batches_back(total_limit, max_available_offset)
    ]
    tasks = list(map(asyncio.create_task, tasks))

    all_comments = list(chain.from_iterable(await asyncio.gather(*tasks)))
    all_comments.sort(key=operator.attrgetter('comment_date'), reverse=True)
    return all_comments[:total_limit]


async def _fetch_page(limit: int, offset: int, lock: Semaphore) -> dict:
    """Fetch one page of comments and return structured comments list."""
    request_params = {
        'include': 'article_path,article_title,user',
        'order_by': 'date_added',
        'offset': offset,
        'limit': limit,
        'unsafe': 'true',
    }

    timeout = aiohttp.ClientTimeout(total=CONNECTIONS_TIMEOUT)
    conn = aiohttp.TCPConnector(ttl_dns_cache=CONNECTIONS_DNS_CACHE)
    async with lock:
        async with aiohttp.ClientSession(timeout=timeout, connector=conn) as session:
            async with session.get(f'{API_HOST}{API_ENDPOINT_COMMENTS}', params=request_params) as resp:
                logging.info(f'fetch comments req_par={request_params} with code={resp.status}')
                resp.raise_for_status()
                return await resp.json()


async def fetch_comments_page(limit: int, offset: int, lock: Semaphore) -> Iterable[Comment]:
    resp = await _fetch_page(limit, offset, lock)
    return map(parse_comment, resp.get('data', []))


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
    yield from [
        (start_offset + API_COMMENTS_PER_PAGE * factor, API_COMMENTS_PER_PAGE if not num else 1)
        for num, factor in enumerate(factors)
    ]


async def fetch_comments_page_next_offset(limit: int, offset: int, lock: Semaphore) -> Optional[int]:
    comments: list = (await _fetch_page(limit, offset, lock)).get('data', [])
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
