from tj_feed.grabber.parser import User
from tj_feed.grabber.scrapper import _fetch_users_page, fetch_top_users


async def test_fetch_users_page():
    result = list(await _fetch_users_page(10, 18))

    assert len(result) == 10
    assert all(map(lambda x: isinstance(x, User), result))
    assert result[0].karma > result[1].karma


async def test_fetch_top_users():
    result = await fetch_top_users(17)

    assert len(result) == 17
    assert result[0].karma > result[1].karma
