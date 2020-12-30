import logging

from starlette.applications import Starlette
from starlette.routing import Route

from tj_feed.feed import last_comments
from tj_feed.storage import close_conn, create_conn

webapp = Starlette(debug=False, routes=[
    Route('/', last_comments, methods=['GET']),
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
