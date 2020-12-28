"""
Скраппер journal.tinkoff.ru

"""
import asyncio
import logging
import operator
import unicodedata
from asyncio import Semaphore
from dataclasses import dataclass
from itertools import chain
from typing import List, Optional, Tuple

import aiohttp
from typed_json_dataclass import TypedJsonMixin

HOST = 'https://journal.tinkoff.ru'
API_HOST = 'https://social.journal.tinkoff.ru'
API_ENDPOINT_COMMENTS = '/api/v13/comments/'

DEFAULT_AVATAR = 'https://static2.tinkoffjournal.ru/mercury-front/fbfb8fb7b8ce70bf9516d9028e231419853c5444/face-08.982a.png'

MAX_CONCURRENT_CONNECTIONS = Semaphore(5)
CONNECTION_TIMEOUT = 20

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


def parse_comment(comment: dict) -> Comment:
    def remove_control_characters(s):
        return "".join(ch for ch in s if unicodedata.category(ch)[0] != "C")

    def unicode_normalize(v: str) -> str:
        try:
            v = v.replace(u"\xa0", u" ")
        except AttributeError:
            return ''
        return remove_control_characters(v)

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


def combine_batches(total_limit: int, max_offset: int) -> Tuple[int, int]:
    offset_start = max(0, max_offset - total_limit)
    for local_offset in range(offset_start, max(max_offset, API_COMMENTS_PER_PAGE), API_COMMENTS_PER_PAGE):
        yield local_offset, API_COMMENTS_PER_PAGE


async def fetch_last_comments(total_limit: int, max_available_offset: int) -> List[Comment]:
    tasks = [asyncio.create_task(fetch_comments_page(local_limit, local_offset, MAX_CONCURRENT_CONNECTIONS))
             for local_offset, local_limit in combine_batches(total_limit, max_available_offset)]

    all_comments = list(chain.from_iterable(
        await asyncio.gather(*tasks)))
    all_comments.sort(key=operator.attrgetter('comment_date'), reverse=True)
    logging.info('fetch %d comments', len(all_comments))
    return all_comments[:total_limit]


async def fetch_comments_page(limit: int, offset: int, lock: Semaphore = None) -> List[Comment]:
    """
    Fetch one page of comments and return structured comments list

    """

    if not lock:
        lock = Semaphore(9999)

    url = f'{API_HOST}{API_ENDPOINT_COMMENTS}'
    params = {
        'include': 'article_path,article_title,user',
        'order_by': 'date_added',
        'offset': offset,
        'limit': limit,
        'unsafe': 'true'
    }

    timeout = aiohttp.ClientTimeout(total=CONNECTION_TIMEOUT)
    conn = aiohttp.TCPConnector(ttl_dns_cache=300)
    async with lock:
        async with aiohttp.ClientSession(timeout=timeout, connector=conn) as session:
            async with session.get(url, params=params) as resp:
                logging.info(f'fetch comments {params=} with {resp.status=}')
                resp.raise_for_status()
                raw_response = await resp.json()
                return list(map(parse_comment, raw_response.get('data', [])))
