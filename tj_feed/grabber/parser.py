import unicodedata
from dataclasses import dataclass
from typing import Optional

from typed_json_dataclass import TypedJsonMixin

HOST = 'https://journal.tinkoff.ru'
DEFAULT_AVATAR = 'https://static2.tinkoffjournal.ru/mercury-front/fbfb8fb7b8ce70bf9516d9028e231419853c5444/face-08.982a.png'


class UserLinkMixin(object):
    user_id: int

    @property
    def user_link(self) -> str:
        return '{0}/user{1}/'.format(HOST, str(self.user_id))


@dataclass
class Comment(TypedJsonMixin, UserLinkMixin):
    user_id: int
    user_name: str
    user_image: Optional[str]

    comment_id: int
    comment_content: str
    comment_date: str
    comment_rating: int

    article_path: str
    article_title: str

    @property
    def comment_link(self) -> str:
        return '{0}{1}#c{2}'.format(HOST, self.article_path, str(self.comment_id))


@dataclass
class User(TypedJsonMixin, UserLinkMixin):
    user_id: int
    badges: str
    comments_count: int
    image: Optional[str]
    karma: int
    name: str

    @property
    def avg_rating_per_comment(self) -> float:
        if not self.comments_count:
            return self.karma

        return self.karma / self.comments_count


def unicode_normalize(source: str) -> str:
    try:
        source = source.replace('\xa0', ' ')
    except AttributeError:
        return ''

    filtered_chars = filter(lambda char: unicodedata.category(char)[0] != 'C', source)
    return ''.join(filtered_chars)


def parse_comment(comment: dict) -> Comment:
    user: dict = comment.get('author', {}) if comment.get('author') else {}
    rating: dict = comment.get('rating', {})
    return Comment(
        user_id=int(user.get('id', 0)),
        user_name=unicode_normalize(user.get('name', 'unknown')),
        user_image=user.get('image') if user.get('image') else DEFAULT_AVATAR,
        comment_id=int(str(comment.get('id'))),
        comment_content=unicode_normalize(str(comment.get('text'))),
        comment_date=str(comment.get('date_added')),
        comment_rating=rating.get('likes', 0) - rating.get('dislikes', 0),
        article_title=unicode_normalize(str(comment.get('article_title'))),
        article_path=str(comment.get('article_path')),
    )


def parse_user(user: dict) -> User:
    badge = user.get('badge', {})
    return User(
        user_id=int(user.get('id', 0)),
        badges=str(badge.get('text', '')) if badge else '',
        comments_count=int(user.get('comments_shown_count', 0)),
        image=user.get('image') if user.get('image') else DEFAULT_AVATAR,
        karma=user.get('karma', 0),
        name=unicode_normalize(str(user.get('name', 'unknown'))),
    )
