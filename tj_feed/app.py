import logging

from starlette.applications import Starlette
from starlette.routing import Route

from tj_feed.feed import last_comments_txt, last_comments_html, top_users_html, top_users_export
from tj_feed.storage import close_conn, create_conn

webapp = Starlette(debug=False, routes=[
    Route('/', last_comments_html, methods=['GET'], name="homepage"),
    Route('/export', last_comments_txt, methods=['GET'], name="comments export"),
    Route('/top', top_users_html, methods=['GET'], name="user rating"),
    Route('/top/export', top_users_export, methods=['GET'], name='user rating export'),
])

logger = logging.getLogger()
app_log = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(process)s %(levelname)s %(name)s %(message)s')  # noqa: WPS323
app_log.setFormatter(formatter)
logger.handlers = []
logger.addHandler(app_log)
logger.setLevel(logging.INFO)


@webapp.on_event('startup')
async def startup():
    await create_conn()
    logging.info('connect to redis')


@webapp.on_event('shutdown')
async def shutdown():
    await close_conn()
    logging.info('connect to redis closed')
