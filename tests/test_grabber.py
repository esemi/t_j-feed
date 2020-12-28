import pytest

from app.grabber import parse_comment, Comment, fetch_comments_page, fetch_last_comments, combine_batches, API_COMMENTS_PER_PAGE


def test_comment_parser():
    source = {"id": 265962, "parent_id": None, "date_added": "2020-10-15T11:22:08.210391+03:00", "is_edited": False, "level": 0,
              "text": "рандомный текст",
              "author": {"id": 46794, "name": "Мария Илюхина", "badge": None, "participation": [], "image": "https://sun9--w0&ava=1", "ban": None},
              "rating": {"likes": 1, "dislikes": 0, "user_vote": 0}, "status": "visible", "article_path": "/diary-businessman-podmoskovie-920k/",
              "article_title": "Как живет предприниматель в Подмосковье с доходом 920 000 ₽", "ban": None, "image": None}

    result = parse_comment(source)

    assert isinstance(result, Comment)
    assert result.comment_date == '2020-10-15T11:22:08.210391+03:00'
    assert result.comment_content == 'рандомный текст'
    assert result.comment_id == 265962
    assert result.comment_link == 'https://journal.tinkoff.ru/diary-businessman-podmoskovie-920k/#c265962'

    assert result.article_path == '/diary-businessman-podmoskovie-920k/'
    assert result.article_title == 'Как живет предприниматель в Подмосковье с доходом 920 000 ₽'

    assert result.user_id == 46794
    assert result.user_name == 'Мария Илюхина'
    assert result.user_link == 'https://journal.tinkoff.ru/user46794/'
    assert result.user_image == 'https://sun9--w0&ava=1'


@pytest.mark.asyncio
async def test_fetch_comments_page():
    result = await fetch_comments_page(10, 18)
    assert len(result) == 10
    assert all(map(lambda x: isinstance(x, Comment), result))
    assert result[0].comment_id < result[1].comment_id


@pytest.mark.asyncio
async def test_fetch_last_comments():
    result = await fetch_last_comments(2, 0)

    assert len(result) == 2
    assert result[0].comment_id > result[1].comment_id


@pytest.mark.parametrize("total_limit,max_offset,expected", [
    (2000, 1340, [(0, API_COMMENTS_PER_PAGE)]),
    (4000, 13400, [(9400, API_COMMENTS_PER_PAGE), (11400, API_COMMENTS_PER_PAGE)]),
    (1, 134, [(133, API_COMMENTS_PER_PAGE)]),
    (100, 0, [(0, API_COMMENTS_PER_PAGE)]),
    (10, 2005, [(1995, API_COMMENTS_PER_PAGE)]),
    (2001, 278901, [(276900, API_COMMENTS_PER_PAGE), (278900, API_COMMENTS_PER_PAGE)]),
])
def test_combine_batches(total_limit: int, max_offset: int, expected: list):
    res = list(combine_batches(total_limit, max_offset))

    assert res == expected
