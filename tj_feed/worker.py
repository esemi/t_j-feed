"""Background scrapper."""
import asyncio
import logging

from tj_feed import settings, storage
from tj_feed.grabber import scrapper

logger = logging.getLogger(__name__)


async def main() -> None:
    """Run background caller worker."""
    logger.info('scrapper started')
    top_users = await scrapper.fetch_top_users(settings.USERS_LIMIT_MAX)
    logging.info('fetch %d users by karma', len(top_users))  # noqa: WPS323
    if top_users:
        await storage.update_top(top_users)
    logger.info('scrapper stopped')


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',  # noqa: WPS323
    )
    asyncio.run(main())
