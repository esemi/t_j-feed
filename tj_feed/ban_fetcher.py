import asyncio
import logging

from tj_feed.grabber.scrapper import fetch_top_users

LIMIT: int = 4500


async def main(limit: int):
    all_users = await fetch_top_users(limit)

    baned_users = [
        user
        for user in all_users
        if user.ban
    ]
    today_banned = [
        user
        for user in baned_users
        if '2023-12-29' in user.ban
    ]
    logging.info('Total banned: {0}'.format(len(baned_users)))
    for user_banned in baned_users:
        logging.info(f'{user_banned.name} {user_banned.ban}')

    logging.info('Today banned: {0}'.format(len(today_banned)))
    for user_banned_today in today_banned:
        logging.info(f'{user_banned_today.name} {user_banned_today.ban}')


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',  # noqa: WPS323
    )
    asyncio.run(main(LIMIT))
