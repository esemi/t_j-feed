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
from starlette.templating import Jinja2Templates
from typed_json_dataclass import TypedJsonMixin

HOST = 'https://journal.tinkoff.ru'
API_HOST = 'https://social.journal.tinkoff.ru'
API_ENDPOINT_COMMENTS = '/api/public/v2.4/comments'
DEFAULT_AVATAR = 'https://static2.tinkoffjournal.ru/mercury-front/fbfb8fb7b8ce70bf9516d9028e231419853c5444/face-08.982a.png'

API_COMMENTS_LIMIT = 100
MAX_CONN = 5
CONN_TIMEOUT = 15
RSS_PAGES_LIMIT = 50
HTML_PAGES_LIMIT = 5

templates = Jinja2Templates(directory='templates')


@dataclass
class Comment(TypedJsonMixin):
    user_id: int
    user_name: str
    user_grade: str
    user_image: str

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
        try:
            v = v.replace(u"\xa0", u" ")
        except AttributeError:
            return ''
        return v

    user = comment.get('user', {})
    if not user.get('image'):
        logging.info('empty user found %s', user)

    return Comment(
        user_id=int(user.get('id')),
        user_name=unicode_normalize(user.get('name')),
        user_grade=unicode_normalize(user.get('grade')),
        user_image=user.get('image') if user.get('image') else DEFAULT_AVATAR,
        comment_id=int(comment.get('id')),
        comment_content=comment.get('text'),
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
    fg.link(href='http://tj.esemi.ru/feed.rss', rel='self')
    fg.language('ru')
    fg.updated(comments[0].comment_date)

    for entity in comments:
        fe = fg.add_entry(order='append')
        fe.author(author={'name': f'{entity.user_name} [{entity.user_grade}]', 'uri': entity.user_link})
        fe.link(href=entity.comment_link)
        fe.title(f'{entity.article_title[:100]}...')
        fe.content(entity.comment_content)
        fe.updated(entity.comment_date)
        fe.id(entity.comment_link)

    return fg.atom_str(pretty=True)


async def fetch_comments(pages_count: int) -> List[Comment]:
    max_conn_lock = Semaphore(MAX_CONN)
    comments_tasks = [asyncio.create_task(fetch_comments_page(i, max_conn_lock)) for i in
                      range(pages_count, 0, -1)]
    all_comments = list(chain.from_iterable(
        await asyncio.gather(*comments_tasks)))
    all_comments.sort(key=operator.attrgetter('comment_id'), reverse=True)
    logging.info('fetch %d comments', len(all_comments))
    return all_comments


async def html_feed(request):
    logging.info('html feed request')
    all_comments = await fetch_comments(HTML_PAGES_LIMIT)

    return templates.TemplateResponse('index.html', {'request': request, 'comments': all_comments})


async def rss_feed(request):
    logging.info('rss feed request')

    # fetch last 1000 comments for feed
    all_comments = await fetch_comments(RSS_PAGES_LIMIT)

    # prepare rss feed
    feed_content = generate_atom_feed(all_comments)
    logging.info('generate atom feed %d length', len(feed_content))

    return PlainTextResponse(feed_content, media_type='application/atom+xml; charset=utf-8')


logger = logging.getLogger()
app_log = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(process)s %(levelname)s %(name)s %(message)s')
app_log.setFormatter(formatter)
logger.handlers = []
logger.addHandler(app_log)
logger.setLevel(logging.INFO)

app = Starlette(debug=False, routes=[
    Route('/feed.rss', rss_feed, methods=["GET"]),
    Route('/', html_feed, methods=["GET"]),
])
