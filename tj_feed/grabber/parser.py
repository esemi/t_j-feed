import unicodedata
from dataclasses import dataclass
from typing import Optional

from typed_json_dataclass import TypedJsonMixin  # type: ignore

HOST = 'https://journal.tinkoff.ru'
DEFAULT_AVATAR = 'https://static2.tinkoffjournal.ru/mercury-front/fbfb8fb7b8ce70bf9516d9028e231419853c5444/face-08.982a.png'


@dataclass
class User(TypedJsonMixin):
    user_id: int
    badges: str
    comments_count: int
    image: Optional[str]
    karma: int
    karma_by_comments: int
    name: str
    ban: str

    @property
    def avg_rating_per_comment(self) -> float:
        if not self.comments_count:
            return self.karma_by_comments

        return self.karma_by_comments / self.comments_count

    @property
    def user_link(self) -> str:
        return '{0}/user{1}/'.format(HOST, str(self.user_id))


def unicode_normalize(source: str) -> str:
    try:
        source = source.replace('\xa0', ' ')
    except AttributeError:
        return ''

    filtered_chars = filter(lambda char: unicodedata.category(char)[0] != 'C', source)
    return ''.join(filtered_chars)


def parse_user(user: dict) -> User:
    badge = user.get('badge', {}) or {}
    ban = user.get('ban', {}) or {}
    karma = user.get('karma', 0) or 0
    karma_by_comments = user.get('karma_actions', {}) or {}
    return User(
        user_id=int(user.get('id', 0)),
        badges=str(badge.get('text', '')) if badge else '',
        comments_count=int(user.get('comments_shown_count', 0)),
        image=user.get('image') if user.get('image') else DEFAULT_AVATAR,
        karma=karma,
        karma_by_comments=karma_by_comments.get('comments', karma) or 0,
        name=unicode_normalize(str(user.get('name', 'unknown'))),
        ban=ban.get('started_at', '') if ban else '',
    )
