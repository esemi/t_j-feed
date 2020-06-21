import asyncio
import logging
import operator
from asyncio import Semaphore
from dataclasses import dataclass
from itertools import chain
from typing import List

import aiohttp
from feedgen.feed import FeedGenerator
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
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
    def unicode_normalize(v: str) -> str:
        v = v.replace(u"\xa0", u" ")
        return v
    user = comment.get('user', {})
    return Comment(
        user_id=int(user.get('id')),
        user_name=unicode_normalize(user.get('name')),
        user_grade=unicode_normalize(user.get('grade')),
        comment_id=int(comment.get('id')),
        comment_content=unicode_normalize(comment.get('text')),
        comment_date=comment.get('date_added'),
        article_title=unicode_normalize(comment.get('article_title')),
        article_path=comment.get('article_path'),
    )


async def fetch_comments_page(page: int, lock: Semaphore = None) -> List[Comment]:
    """
    Fetch one page of comments and return structured comments list

    """

    if not lock:
        lock = Semaphore(9999)

    url = f'{API_HOST}{API_ENDPOINT_COMMENTS}'
    params = {
        'include': 'article_path,article_title,user',
        'order_by': 'date_added',
        'order_direction': 'desc',
        'offset': API_COMMENTS_LIMIT * (page - 1),
        'limit': API_COMMENTS_LIMIT,
        'unsafe': 'true'
    }

    timeout = aiohttp.ClientTimeout(total=CONN_TIMEOUT)
    conn = aiohttp.TCPConnector(ttl_dns_cache=300)
    async with lock:
        async with aiohttp.ClientSession(timeout=timeout, connector=conn) as session:
            async with session.get(url, params=params) as resp:
                logging.info('fetch %d page with code=%s', page, resp.status)
                logging.info(f'{params=}')
                resp.raise_for_status()
                comments = (await resp.json())['data']
                return list(map(parse_comment, comments))


def generate_atom_feed(comments: List[Comment]) -> str:
    fg = FeedGenerator()
    fg.id('http://journal.tinkoff.ru')
    fg.logo('https://sun9-20.userapi.com/c846419/v846419100/1e1b58/pxgU8F6HViA.jpg?ava=1')
    fg.title('Т_Ж комменты')
    fg.link(href='http://journal.tinkoff.ru', rel='alternate')
    fg.link(href='http://t_j.esemi.ru/feed.atom', rel='self')
    fg.language('ru')
    fg.updated(comments[0].comment_date)

    for entity in comments:
        fe = fg.add_entry(order='append')
        fe.author(author={'name': f'{entity.user_name} [{entity.user_grade}]', 'uri': entity.user_link})
        fe.link(href=entity.comment_link)
        fe.title(f'{entity.comment_content[:60]}...')
        fe.content(f"{entity.article_title[:100]}...':\n{entity.comment_content}")
        fe.updated(entity.comment_date)
        fe.id(entity.comment_link)

    return fg.atom_str(pretty=True)


async def rss_feed(request):
    logging.info('request fetch %d pages of comments', COMMENTS_PAGES_LIMIT)

    # fetch last 1000comments
    max_conn_lock = Semaphore(MAX_CONN)
    comments_tasks = [asyncio.create_task(fetch_comments_page(i, max_conn_lock)) for i in
                      range(COMMENTS_PAGES_LIMIT, 0, -1)]
    all_comments = list(chain.from_iterable(
        await asyncio.gather(*comments_tasks)))
    all_comments.sort(key=operator.attrgetter('comment_id'), reverse=True)
    logging.info('fetch %d comments', len(all_comments))

    # prepare rss feed
    feed_content = generate_atom_feed(all_comments)
    logging.info('generate atom feed %d length', len(feed_content))

    return PlainTextResponse(feed_content, media_type='application/atom+xml; charset=utf-8')


app = Starlette(debug=False, routes=[
    Route('/', rss_feed, methods=["GET"]),
])
