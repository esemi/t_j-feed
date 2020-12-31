from asyncio import Semaphore

import pytest

from tj_feed.grabber import parse_comment, Comment, fetch_comments_page, fetch_last_comments, combine_batches_back, API_COMMENTS_PER_PAGE, combine_batches_forward, _fetch_page, \
    fetch_comments_page_next_offset, search_local_max_offset, search_actual_offset
from tj_feed.storage import create_conn


def test_comment_parser():
    source = {"id": 265962, "parent_id": None, "date_added": "2020-10-15T11:22:08.210391+03:00", "is_edited": False, "level": 0,
              "text": "рандомный текст",
              "author": {"id": 46794, "name": "Мария Илюхина", "badge": None, "participation": [], "image": "https://sun9--w0&ava=1", "ban": None},
              "rating": {"likes": 1, "dislikes": 17, "user_vote": 0}, "status": "visible", "article_path": "/diary-businessman-podmoskovie-920k/",
              "article_title": "Как живет предприниматель в Подмосковье с доходом 920 000 ₽", "ban": None, "image": None}

    result = parse_comment(source)

    assert isinstance(result, Comment)
    assert result.comment_date == '2020-10-15T11:22:08.210391+03:00'
    assert result.comment_content == 'рандомный текст'
    assert result.comment_id == 265962
    assert result.comment_rating == 1-17
    assert result.comment_link == 'https://journal.tinkoff.ru/diary-businessman-podmoskovie-920k/#c265962'

    assert result.article_path == '/diary-businessman-podmoskovie-920k/'
    assert result.article_title == 'Как живет предприниматель в Подмосковье с доходом 920 000 ₽'

    assert result.user_id == 46794
    assert result.user_name == 'Мария Илюхина'
    assert result.user_link == 'https://journal.tinkoff.ru/user46794/'
    assert result.user_image == 'https://sun9--w0&ava=1'


@pytest.mark.asyncio
async def test_fetch_comments_page():
    lock = Semaphore(9999)

    result = list(await fetch_comments_page(10, 18, lock))

    assert len(result) == 10
    assert all(map(lambda x: isinstance(x, Comment), result))
    assert result[0].comment_id < result[1].comment_id


@pytest.mark.asyncio
async def test_search_local_max_offset(mocker):
    mocker.patch('tj_feed.grabber.combine_batches_forward', lambda x: [(x, 1), (x + 100, 1)])

    result = await search_local_max_offset(456)

    assert result == 456 + 100 + 1


@pytest.mark.asyncio
async def test_search_actual_offset(mocker):
    mocker.patch('tj_feed.grabber.search_local_max_offset', return_value=1457)

    result = await search_actual_offset(456)

    assert result == 1457


@pytest.mark.asyncio
async def test_fetch_comments_page_next_offset(mocker):
    mocker.patch('tj_feed.grabber._fetch_page', return_value=dict())
    result = await fetch_comments_page_next_offset(2, 7, Semaphore(1))
    assert result == 0

    mocker.patch('tj_feed.grabber._fetch_page', return_value=dict(data=[1, 2, 3]))
    result = await fetch_comments_page_next_offset(2, 7, Semaphore(1))
    assert result == 7 + 3


@pytest.mark.asyncio
async def test_fetch_last_comments():
    result = await fetch_last_comments(2, 0)

    assert len(result) == 2
    assert result[0].comment_id > result[1].comment_id


@pytest.mark.asyncio
async def test_fetch_page():
    result = await _fetch_page(2, 7, Semaphore(1))

    assert isinstance(result, dict)
    data = result.get('data')
    assert isinstance(data, list)
    assert len(data) == 2
    assert 'id' in data[0]
    assert 'date_added' in data[0]
    assert 'text' in data[0]
    assert 'author' in data[0]
    assert 'rating' in data[0]
    assert 'article_path' in data[0]
    assert 'article_title' in data[0]


@pytest.mark.parametrize("total_limit,max_offset,expected", [
    (2000, 1340, [(0, API_COMMENTS_PER_PAGE)]),
    (4000, 13400, [(9400, API_COMMENTS_PER_PAGE), (11400, API_COMMENTS_PER_PAGE)]),
    (1, 134, [(133, API_COMMENTS_PER_PAGE)]),
    (100, 0, [(0, API_COMMENTS_PER_PAGE)]),
    (10, 2005, [(1995, API_COMMENTS_PER_PAGE)]),
    (2001, 278901, [(276900, API_COMMENTS_PER_PAGE), (278900, API_COMMENTS_PER_PAGE)]),
])
def test_combine_batches(total_limit: int, max_offset: int, expected: list):
    res = list(combine_batches_back(total_limit, max_offset))

    assert res == expected


@pytest.mark.parametrize("start_offset,expected", [
    (178, [(178, 2000), (2178, 1), (6178, 1), (10178, 1), (16178, 1), (26178, 1), (42178, 1), (68178, 1), (110178, 1)]),
])
def test_combine_batches_forward(start_offset: int, expected: list):
    res = list(combine_batches_forward(start_offset))

    assert res == expected
