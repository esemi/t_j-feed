import unicodedata
from dataclasses import dataclass
from typing import Optional

from typed_json_dataclass import TypedJsonMixin


HOST = 'https://journal.tinkoff.ru'
DEFAULT_AVATAR = 'https://static2.tinkoffjournal.ru/mercury-front/fbfb8fb7b8ce70bf9516d9028e231419853c5444/face-08.982a.png'


@dataclass
class Comment(TypedJsonMixin):
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
        return f'{HOST}{self.article_path}#c{str(self.comment_id)}'

    @property
    def user_link(self) -> str:
        return f'{HOST}/user{str(self.user_id)}/'


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
        comment_id=int(comment.get('id')),
        comment_content=unicode_normalize(comment.get('text')),
        comment_date=comment.get('date_added'),
        comment_rating=rating.get('likes', 0) - rating.get('dislikes', 0),
        article_title=unicode_normalize(comment.get('article_title')),
        article_path=comment.get('article_path'),
    )
