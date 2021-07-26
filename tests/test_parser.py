from tj_feed.grabber.parser import unicode_normalize, parse_user, User


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


def test_unicode_normalize_smoke():
    assert unicode_normalize('\xa0U+0550test\n') == ' U+0550test'
