import logging
import pathlib

from starlette.templating import Jinja2Templates

from tj_feed import grabber, storage

COMMENTS_LIMIT_DEFAULT = 100
COMMENTS_LIMIT_MAX = 10000


html_templates = Jinja2Templates(directory=pathlib.Path(__file__).parent.joinpath('templates').absolute())


async def last_comments(request):
    logging.info('last comments fetch request')

    # todo update max offset here

    try:
        total_limits = int(request.query_params.get('l', default=COMMENTS_LIMIT_DEFAULT))
    except ValueError:
        total_limits = COMMENTS_LIMIT_DEFAULT

    total_limits = min(COMMENTS_LIMIT_MAX, total_limits)

    max_offset = await storage.get_max_offset(default=0)
    logging.info(f'max_offset={max_offset} total_limits={total_limits}')
    all_comments = await grabber.fetch_last_comments(total_limits, max_offset)

    return html_templates.TemplateResponse('index.html', {'request': request, 'comments': all_comments, 'last_offset': max_offset})
