import logging
import pathlib
from typing import List

from starlette.responses import StreamingResponse
from starlette.templating import Jinja2Templates

from tj_feed import storage
from tj_feed.grabber import scrapper
from tj_feed.grabber.parser import Comment

LIMIT_DEFAULT = 100
LIMIT_MAX = 20000


html_templates = Jinja2Templates(directory=pathlib.Path(__file__).parent.joinpath('templates').absolute())


async def last_comments(total_limits: int) -> List[Comment]:
    current_max_offset = await storage.get_max_offset(default=0)
    logging.info(f'current_max_offset={current_max_offset}')

    max_offset = await scrapper.search_actual_offset(current_max_offset)
    logging.info(f'max_offset={max_offset} total_limits={total_limits}')

    all_comments = await scrapper.fetch_last_comments(total_limits, max_offset)
    logging.info(f'fetch {len(all_comments)} comments')

    return all_comments


async def index_html(request):
    logging.info('last comments html request')

    try:
        total_limits = int(request.query_params.get('l', default=LIMIT_DEFAULT))
    except ValueError:
        total_limits = LIMIT_DEFAULT

    all_comments = await last_comments(min(LIMIT_MAX, total_limits))

    return html_templates.TemplateResponse('index.html', {
        'request': request,
        'comments': all_comments,
        'last_offset': await storage.get_max_offset(default=0),
    })


async def top_users_html(request):
    # todo unittest
    logging.info('top users html request')

    try:
        total_limits = int(request.query_params.get('l', default=LIMIT_DEFAULT))
    except ValueError:
        total_limits = LIMIT_DEFAULT

    top_users = await scrapper.fetch_top_users(min(LIMIT_MAX, total_limits))
    logging.info(f'fetch {len(top_users)} users by karma')

    return html_templates.TemplateResponse('top.html', {
        'request': request,
        'users': top_users
    })


def comment_to_string(comment: Comment) -> str:
    return '\n'.join([
        f'\n{comment.article_title}',
        f'>> {comment.user_name}: {comment.comment_content}',
        f'>> {comment.comment_link}\n',
    ])


async def feed_txt(request):
    logging.info('last comments feed.txt request')
    all_comments = await last_comments(LIMIT_MAX)

    return StreamingResponse(map(comment_to_string, all_comments), media_type='text/plain')
