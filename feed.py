import asyncio
import logging
from asyncio import Semaphore
from dataclasses import dataclass
from itertools import chain
from typing import List

import aiohttp
from starlette.applications import Starlette
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient
from typed_json_dataclass import TypedJsonMixin


HOST = 'https://journal.tinkoff.ru'
API_HOST = 'https://social.journal.tinkoff.ru'
API_ENDPOINT_COMMENTS = '/api/public/v2.4/comments'

API_COMMENTS_LIMIT = 100
MAX_CONN = 5
CONN_TIMEOUT = 15
COMMENTS_PAGES_LIMIT = 10


@dataclass
class Comment(TypedJsonMixin):
    user_id: int
    user_name: str
    user_grade: str

    comment_id: int
    comment_content: str
    comment_date: str

    article_path: str
    article_title: str

    @property
    def comment_link(self) -> str:
        return f'{HOST}{self.article_path}#c{str(self.comment_id)}'

    @property
    def user_link(self) -> str:
        return f'{HOST}/user{str(self.user_id)}/'


def parse_comment(comment: dict) -> Comment:
    user = comment.get('user', {})
    return Comment(
        user_id=int(user.get('id')),
        user_name=user.get('name'),
        user_grade=user.get('grade'),
        comment_id=int(comment.get('id')),
        comment_content=comment.get('text'),
        comment_date=comment.get('date_added'),
        article_title=comment.get('article_title'),
        article_path=comment.get('article_path'),
    )


async def fetch_comments_page(lock: Semaphore, page: int) -> List[Comment]:
    """
    Fetch one page of comments and return structured comments list

    """

    url = f'{API_HOST}{API_ENDPOINT_COMMENTS}'
    params = {
        'include': 'article_path,article_title,user',
        'order_by': 'date_added',
        'order_direction': 'desc',
        'offset': API_COMMENTS_LIMIT * page,
        'limit': API_COMMENTS_LIMIT,
        'unsafe': 'true'
    }

    timeout = aiohttp.ClientTimeout(total=CONN_TIMEOUT)
    conn = aiohttp.TCPConnector(ttl_dns_cache=300)
    async with lock:
        async with aiohttp.ClientSession(timeout=timeout, connector=conn) as session:
            async with session.get(url, params=params) as resp:
                logging.info('fetch %d page with code=%s', page, resp.status)
                resp.raise_for_status()
                comments = (await resp.json())['data']
                return list(map(parse_comment, comments))


async def rss_feed(request):
    logging.info('request fetch %d pages of comments', COMMENTS_PAGES_LIMIT)

    # fetch last 1000comments
    max_conn_lock = Semaphore(MAX_CONN)
    comments_tasks = [asyncio.create_task(fetch_comments_page(max_conn_lock, i)) for i in range(COMMENTS_PAGES_LIMIT)]
    all_comments = list(chain.from_iterable(
        await asyncio.gather(*comments_tasks)))
    logging.info('fetch %d comments', len(all_comments))

    # todo prepare rss feed
    # print(all_comments)

    return PlainTextResponse({'comments': [i.to_json() for i in all_comments]})


app = Starlette(debug=False, routes=[
    Route('/', rss_feed, methods=["GET"]),
])
