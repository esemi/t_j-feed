import logging
import pathlib
from typing import List

from starlette.responses import StreamingResponse
from starlette.templating import Jinja2Templates

from tj_feed import storage
from tj_feed.grabber import scrapper
from tj_feed.grabber.parser import Comment, User

LIMIT_DEFAULT = 100
COMMENTS_LIMIT_MAX = 10000
USERS_LIMIT_MAX = 1000


html_templates = Jinja2Templates(directory=str(
    pathlib.Path(__file__).parent.joinpath('templates').absolute(),
))


async def last_comments(total_limits: int) -> List[Comment]:
    current_max_offset = await storage.get_max_offset(default=0)
    logging.info(f'current_max_offset={current_max_offset}')

    max_offset = await scrapper.search_actual_offset(current_max_offset)
    logging.info(f'max_offset={max_offset} total_limits={total_limits}')

    all_comments = await scrapper.fetch_last_comments(total_limits, max_offset)
    logging.info('fetch {0} comments', len(all_comments))

    return all_comments


async def last_comments_html(request):
    logging.info('last comments html request')

    try:
        total_limits = int(request.query_params.get('l', default=LIMIT_DEFAULT))
    except ValueError:
        total_limits = LIMIT_DEFAULT

    all_comments = await last_comments(min(COMMENTS_LIMIT_MAX, total_limits))

    return html_templates.TemplateResponse('index.html', {
        'request': request,
        'comments': all_comments,
        'last_offset': await storage.get_max_offset(default=0),
    })


async def top_users_html(request):
    logging.info('top users html request')

    try:
        total_limits = int(request.query_params.get('l', default=LIMIT_DEFAULT))
    except ValueError:
        total_limits = LIMIT_DEFAULT

    total_limits = min(USERS_LIMIT_MAX, total_limits)
    top_users = await scrapper.fetch_top_users(total_limits)
    logging.info('fetch {0} users by karma', len(top_users))

    return html_templates.TemplateResponse('top.html', {
        'request': request,
        'users': top_users,
        'limit': total_limits,
    })


async def top_users_export(request):
    logging.info('top users export request')

    top_users = await scrapper.fetch_top_users(USERS_LIMIT_MAX)
    logging.info('fetch {0} users by karma', len(top_users))

    users_as_tsv: List[str] = [user_to_tsv(num, user) for num, user in enumerate(top_users)]
    return StreamingResponse(iter(users_as_tsv), media_type='text/plain')


def user_to_tsv(num: int, user: User) -> str:
    return '\t'.join(map(str, [
        num,
        user.name,
        user.karma,
        user.comments_count,
        user.avg_rating_per_comment,
        user.badges,
        '\n',
    ]))


async def last_comments_txt(request):
    logging.info('last comments feed.txt request')
    all_comments = await last_comments(COMMENTS_LIMIT_MAX)

    return StreamingResponse(map(comment_to_string, all_comments), media_type='text/plain')


def comment_to_string(comment: Comment) -> str:
    return '\n'.join([
        f'\n{comment.article_title}',
        f'>> {comment.user_name}: {comment.comment_content}',
        f'>> {comment.comment_link}\n',
    ])
