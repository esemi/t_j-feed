import logging
import pathlib
from typing import List

from starlette.responses import StreamingResponse
from starlette.templating import Jinja2Templates

from tj_feed.grabber import scrapper
from tj_feed.grabber.parser import User

LIMIT_DEFAULT = 100
USERS_LIMIT_MAX = 1000


html_templates = Jinja2Templates(directory=str(
    pathlib.Path(__file__).parent.joinpath('templates').absolute(),
))


async def top_users_html(request):
    logging.info('top users html request')

    try:
        total_limits = int(request.query_params.get('l', default=LIMIT_DEFAULT))
    except ValueError:
        total_limits = LIMIT_DEFAULT

    total_limits = min(USERS_LIMIT_MAX, total_limits)
    top_users = await scrapper.fetch_top_users(total_limits)
    logging.info('fetch %d users by karma', len(top_users))  # noqa: WPS323

    return html_templates.TemplateResponse('top.html', {
        'request': request,
        'users': top_users,
        'limit': total_limits,
    })


async def top_users_export(request):
    logging.info('top users export request')

    top_users = await scrapper.fetch_top_users(USERS_LIMIT_MAX)
    logging.info('fetch %d users by karma', len(top_users))  # noqa: WPS323

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
