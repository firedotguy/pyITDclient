"""Вложенные модели должны попадать к клиенту родителя, а не к дефолтному"""

import pytest
from helpers import make_client, make_token

from itd.models.post import Post

pytestmark = pytest.mark.usefixtures('keep_default_client')

POST = {
    'id': '00000000-0000-0000-0000-0000000000ff',
    'author': {'id': '00000000-0000-0000-0000-000000000001', 'username': 'fires', 'displayName': 'fi.res'},
    'createdAt': '2026-01-30T12:58:14.228Z',
    'content': 'привет',
    'vs': 'view-token',
    'attachments': [{'id': '00000000-0000-0000-0000-00000000000a', 'url': 'u', 'type': 'image', 'width': 1, 'height': 1}],
    'comments': [{
        'id': '00000000-0000-0000-0000-00000000000c',
        'content': 'комментарий',
        'author': {'id': '00000000-0000-0000-0000-000000000001', 'username': 'fires', 'displayName': 'fi.res'},
        'createdAt': '2026-01-30T12:58:14.228Z',
        'attachments': [],
        'likesCount': 0
    }],
    'poll': {
        'id': '00000000-0000-0000-0000-00000000000d',
        'postId': '00000000-0000-0000-0000-0000000000ff',
        'createdAt': '2026-01-30T12:58:14.228Z',
        'question': 'вопрос',
        'isMultiple': False,
        'options': [{'id': '00000000-0000-0000-0000-00000000000e', 'text': 'вариант', 'votesCount': 0, 'position': 0}]
    }
}


@pytest.fixture
def post():
    client = make_client(make_token(900))
    make_client(make_token(900))  # второй клиент: он станет дефолтным, к нему уезжали вложенные модели
    return Post.from_dict(dict(POST), client=client), client


def test_nested_models_share_client(post):
    post, client = post

    assert post.client is client
    assert post.author.client is client
    assert post.attachments[0].client is client
    assert post.comments.client is client
    assert post.first_comments[0].client is client
    assert post.poll.client is client
    assert post.poll.options[0].client is client


def test_back_references_do_not_steal_client(post):
    """comment._post = post не должен отдавать посту клиента комментария"""
    post, client = post

    assert post.comments._post is post
    assert post.first_comments[0]._post is post
    assert post.attachments[0]._post is post
    assert post.client is client


def test_poll_options_know_their_post(post):
    post, _ = post

    assert post.poll.options[0]._post_id == post.poll.post_id
