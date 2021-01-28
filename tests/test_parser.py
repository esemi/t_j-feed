from tj_feed.grabber.parser import parse_comment, Comment, unicode_normalize, parse_user, User


def test_user_parser():
    source = {"id": 5227, "name": "Pavla Tolokonina", "image": "https://graph.facebook.com/v7.0/10154947640836169/picture?type=square&return_ssl_resources=1&height=600&width=600",
              "karma": 21651, "badge": {"type": "custom", "text": "Герой Т—Ж 🏆"}, "extra": {}, "comments_shown_count": 3827,
              "participation": [{"article_title": "От пижамы до робота-пылесоса: список подарков, которые все хотят получить на Новый год",
                                 "article_path": "/my-wish-is/", "role": "hero", "role_description": ""}], "ban": None}

    result = parse_user(source)

    assert isinstance(result, User)
    assert result.user_id == 5227
    assert result.name == 'Pavla Tolokonina'
    assert result.user_link == 'https://journal.tinkoff.ru/user5227/'
    assert result.karma == 21651
    assert result.badges == 'Герой Т—Ж 🏆'
    assert result.comments_count == 3827
    assert result.avg_rating_per_comment == 21651 / 3827
    assert result.image == 'https://graph.facebook.com/v7.0/10154947640836169/picture?type=square&return_ssl_resources=1&height=600&width=600'
    assert result.extra == dict()


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
    assert result.comment_rating == 1 - 17
    assert result.comment_link == 'https://journal.tinkoff.ru/diary-businessman-podmoskovie-920k/#c265962'

    assert result.article_path == '/diary-businessman-podmoskovie-920k/'
    assert result.article_title == 'Как живет предприниматель в Подмосковье с доходом 920 000 ₽'

    assert result.user_id == 46794
    assert result.user_name == 'Мария Илюхина'
    assert result.user_link == 'https://journal.tinkoff.ru/user46794/'
    assert result.user_image == 'https://sun9--w0&ava=1'


def test_regress():
    case = {'id': 299710, 'parent_id': None, 'date_added': '2020-12-02T23:18:23.717576+03:00', 'is_edited': False, 'level': 0,
            'text': 'Удачи автору во всех его начинаниях. По истории сложилось впечатление, что вы не семья, а совместно проживающие люди. И грустно, что партнёру не нравится котик :(',
            'author': None, 'rating': {'likes': 14, 'dislikes': 0, 'user_vote': 0}, 'status': 'visible', 'article_path': '/diary-ordinator-moscow-33k/',
            'article_title': 'Как живет врач-ординатор в\xa0Москве с\xa0доходом 33\xa0400\xa0₽', 'ban': None, 'image': None}

    result = parse_comment(case)
    assert isinstance(result, Comment)


def test_unicode_normalize_smoke():
    assert unicode_normalize('\xa0U+0550test\n') == ' U+0550test'
