import logging

from starlette.applications import Starlette
from starlette.routing import Route

from app.feed import last_comments
from app.storage import create_conn, close_conn

logger = logging.getLogger()
app_log = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(process)s %(levelname)s %(name)s %(message)s')
app_log.setFormatter(formatter)
logger.handlers = []
logger.addHandler(app_log)
logger.setLevel(logging.INFO)

webapp = Starlette(debug=False, routes=[
    Route('/', last_comments, methods=["GET"]),
])


@webapp.on_event('startup')
async def startup():
    await create_conn()
    logging.info('connect to redis')


@webapp.on_event('shutdown')
async def shutdown():
    await close_conn()
    logging.info('connect to redis closed')
