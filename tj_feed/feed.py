import logging
import pathlib

from starlette.templating import Jinja2Templates

from tj_feed import storage
from tj_feed.grabber import scrapper

COMMENTS_LIMIT_DEFAULT = 100
COMMENTS_LIMIT_MAX = 10000


html_templates = Jinja2Templates(directory=pathlib.Path(__file__).parent.joinpath('templates').absolute())


async def last_comments(request):
    logging.info('last comments fetch request')

    try:
        total_limits = int(request.query_params.get('l', default=COMMENTS_LIMIT_DEFAULT))
    except ValueError:
        total_limits = COMMENTS_LIMIT_DEFAULT

    total_limits = min(COMMENTS_LIMIT_MAX, total_limits)

    current_max_offset = await storage.get_max_offset(default=0)
    logging.info(f'current_max_offset={current_max_offset}')

    max_offset = await scrapper.search_actual_offset(current_max_offset)
    logging.info(f'max_offset={max_offset} total_limits={total_limits}')

    all_comments = await scrapper.fetch_last_comments(total_limits, max_offset)
    logging.info(f'fetch {len(all_comments)} comments')

    return html_templates.TemplateResponse('index.html', {'request': request, 'comments': all_comments, 'last_offset': max_offset})
