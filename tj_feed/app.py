import logging

from starlette.applications import Starlette
from starlette.routing import Route

from tj_feed import feed

HTTP_METHOD_GET = 'GET'

webapp = Starlette(debug=False, routes=[
    Route('/', feed.top_users_html, methods=[HTTP_METHOD_GET], name='user rating'),
    Route('/top/export', feed.top_users_export, methods=[HTTP_METHOD_GET], name='user rating export'),
])

logger = logging.getLogger()
app_log = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(process)s %(levelname)s %(name)s %(message)s')  # noqa: WPS323
app_log.setFormatter(formatter)
logger.handlers = []
logger.addHandler(app_log)
logger.setLevel(logging.INFO)
