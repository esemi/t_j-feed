import logging

from starlette.templating import Jinja2Templates

from app import grabber
from app import storage

templates = Jinja2Templates(directory='templates')

COMMENTS_LIMIT_DEFAULT = 100
COMMENTS_LIMIT_MAX = 10000


async def last_comments(request):
    logging.info('last comments fetch request')

    # todo update max offset here

    try:
        total_limits = int(request.query_params.get('l', default=COMMENTS_LIMIT_DEFAULT))
        total_limits = max(COMMENTS_LIMIT_MAX, total_limits)
    except ValueError:
        total_limits = COMMENTS_LIMIT_DEFAULT

    max_offset = await storage.get_max_offset(0)
    logging.info(f'{max_offset=}')
    all_comments = await grabber.fetch_last_comments(total_limits, max_offset)

    return templates.TemplateResponse('index.html', {'request': request, 'comments': all_comments})
