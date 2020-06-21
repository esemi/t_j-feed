import pytest
from starlette.testclient import TestClient

from feed import app, parse_comment, Comment, fetch_comments_page


def test_rss_feed_endpoint():
    client = TestClient(app)
    response = client.get('/')
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_fetch_comments_page():
    result = await fetch_comments_page(1)
    assert len(result) == 100
    assert result[0].comment_id > result[1].comment_id
    assert all(map(lambda x: isinstance(x, Comment), result))


def test_comment_parser():
    source = {'id': 197577, 'parent_id': 197129, 'date_added': '2020-06-20T18:41:34.889094+03:00', 'is_deleted': False,
              'level': 1, 'text': 'рандомный текст', 'rating': {'likes': 1, 'dislikes': 0, 'user_vote': 0},
              'is_public': True, 'is_editors_choice': False, 'article_path': '/news/avtokredit-so-skidkoi-june-2020/',
              'article_title': 'Льготные автокредиты: теперь для\xa0семей с\xa0одним ребенком и\xa0на\xa0машины',
              'user': {'id': 16297, 'name': 'Елизавета Кружкова',
                       'image': 'https://graph.facebook.com/v2.12/5446546465464654/picture?type=square',
                       'karma': 15, 'badge': None, 'is_banned': False, 'banned_for_comment': None, 'extra': None,
                       'comments_shown_count': 4, 'participation': [], 'grade': 'бодрый комментатор, нейтрал',
                       'likes_count': 37, 'dislikes_count': 24, 'actions_useful_count': 65,
                       'date_joined': '2019-03-18T11:50:19.965623+03:00', 'provider': 'facebook'}}
    result = parse_comment(source)
    assert isinstance(result, Comment)
    assert result.comment_date == '2020-06-20T18:41:34.889094+03:00'
    assert result.comment_content == 'рандомный текст'
    assert result.article_path == '/news/avtokredit-so-skidkoi-june-2020/'
    assert result.comment_link == 'https://journal.tinkoff.ru/news/avtokredit-so-skidkoi-june-2020/#c197577'
    assert result.article_title == 'Льготные автокредиты: теперь для\xa0семей с\xa0одним ребенком и\xa0на\xa0машины'
    assert result.comment_id == 197577
    assert result.user_id == 16297
    assert result.user_grade == 'бодрый комментатор, нейтрал'
    assert result.user_name == 'Елизавета Кружкова'
    assert result.user_link == 'https://journal.tinkoff.ru/user16297/'
