"""Ленивая загрузка: модель ходит в апи только за тем, чего в данных не было"""

import pytest
from helpers import make_client, make_token

from itd.models.post import Post

pytestmark = pytest.mark.usefixtures('keep_default_client')

AUTHOR = {'id': '00000000-0000-0000-0000-000000000001', 'username': 'fires', 'displayName': 'fi.res'}
IN_LIST = {  # так пост приходит в списке: ни comments, ни первых комментариев в ответе нет
    'id': '00000000-0000-0000-0000-0000000000ff',
    'author': AUTHOR,
    'createdAt': '2026-01-30T12:58:14.228Z',
    'content': 'привет',
    'attachments': [],
    'likesCount': 1
}
ALONE = IN_LIST | {  # а так - в одиночном ответе
    'comments': [{
        'id': '00000000-0000-0000-0000-00000000000c',
        'content': 'комментарий',
        'author': AUTHOR,
        'createdAt': '2026-01-30T12:58:14.228Z',
        'attachments': [],
        'likesCount': 0
    }]
}


@pytest.fixture
def refreshes(monkeypatch):
    """Считать обращения в апи вместо запросов"""
    calls = []
    monkeypatch.setattr(Post, 'refresh', lambda self, **kwargs: (calls.append(self.id), self)[1])
    return calls


def test_post_from_list_does_not_refresh(refreshes):
    """Пост из списка не должен догружаться сам по себе - раньше _post_refresh дергал first_comments"""
    post = Post.from_dict(dict(IN_LIST), client=make_client(make_token(900)))

    assert refreshes == []
    assert post.is_loaded('content') and post.is_loaded('attachments')
    assert not post.is_loaded('first_comments')


def test_single_post_wires_its_comments(refreshes):
    post = Post.from_dict(dict(ALONE), client=make_client(make_token(900)))

    assert refreshes == []
    assert post.is_loaded('first_comments')
    assert [comment._post for comment in post.first_comments] == [post]


def test_get_loaded_does_not_touch_api(refreshes):
    post = Post.from_dict(dict(IN_LIST), client=make_client(make_token(900)))

    assert post.get_loaded('first_comments', []) == []
    assert post.get_loaded('content') == 'привет'
    assert refreshes == []

    post.first_comments  # а обычное обращение - идет за данными
    assert len(refreshes) == 1
