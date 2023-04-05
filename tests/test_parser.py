from tj_feed.grabber.parser import unicode_normalize, parse_user, User


def test_user_parser():
    source = {"id": 1588146, "name": "Филиппыч",
              "image": "https://opis-cdn.tinkoffjournal.ru/ip/h2kBBKsSBNhP2Z3x9TxzwWKhYUi71E4w1TI1aSU1Zjs/h:600/w:600/aHR0cHM6Ly9vcGlz/LWNkbi50aW5rb2Zm/am91cm5hbC5ydS9z/b2NpYWwvcHJvZmls/ZS8xYjVlZjI0Zi42/YTUwMzlkNV82OTAy/OTZfb3JpZ2luYWwu/anBn",
              "has_default_image": False,
              "karma": 222524,
              "karma_actions": {"comments": 222494,
                                "readers_posts": 30,
                                "editorial_posts": 0,
                                "questions": 0,
                                "bans": 0},
              "badge": {"type": "custom",
                        "text": "Легенда 🎨💫"},
              "extra": {},
              "comments_shown_count": 4020,
              "participation": {
                  "article_title": "Генератор тостов от читателей T—Ж: найдите, чем блеснуть за новогодним столом",
                  "article_path": "/tak-vypem-zhe/",
                  "role": "hero",
                  "role_description": ""},
              "role_participation_count": 7,
              "all_participation_count": 8,
              "ban": None, "bio": None,
              "subscribers_count": 5}

    result = parse_user(source)

    assert isinstance(result, User)
    assert result.user_id == 1588146
    assert result.name == 'Филиппыч'
    assert result.user_link == 'https://journal.tinkoff.ru/user1588146/'
    assert result.karma == 222524
    assert result.karma_by_comments == 222494
    assert result.badges == 'Легенда 🎨💫'
    assert result.comments_count == 4020
    assert result.avg_rating_per_comment == 222494 / 4020
    assert result.image == 'https://opis-cdn.tinkoffjournal.ru/ip/h2kBBKsSBNhP2Z3x9TxzwWKhYUi71E4w1TI1aSU1Zjs/h:600/w:600/aHR0cHM6Ly9vcGlz/LWNkbi50aW5rb2Zm/am91cm5hbC5ydS9z/b2NpYWwvcHJvZmls/ZS8xYjVlZjI0Zi42/YTUwMzlkNV82OTAy/OTZfb3JpZ2luYWwu/anBn'


def test_unicode_normalize_smoke():
    assert unicode_normalize('\xa0U+0550test\n') == ' U+0550test'
