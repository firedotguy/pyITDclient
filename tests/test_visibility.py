"""Таймеры и видимые посты - отдельно от клиента, поэтому проверяются без потоков и без сети"""

from datetime import datetime, timedelta
from time import sleep

import pytest
from helpers import make_client, make_response, make_token

from itd.core.timer import Timer
from itd.core.visibility import VisibilityTracker
from itd.models.post import Post

pytestmark = pytest.mark.usefixtures('keep_default_client')

POST = {
    'id': '00000000-0000-0000-0000-0000000000ff',
    'author': {'id': '00000000-0000-0000-0000-000000000001', 'username': 'fires', 'displayName': 'fi.res'},
    'createdAt': '2026-01-30T12:58:14.228Z',
    'content': 'привет',
    'attachments': [],
    'likesCount': 1,
    'vs': 'view-token'
}


def test_timer_calls_target_and_stops():
    calls = []
    timer = Timer('test', 0.01, lambda: calls.append(1))

    assert timer.start()
    sleep(0.05)
    timer.stop()
    after_stop = len(calls)
    sleep(0.05)

    assert calls, 'таймер ни разу не сработал'
    assert len(calls) == after_stop, 'таймер продолжил работать после stop'
    assert not timer.running


def test_timer_with_zero_interval_does_not_start():
    timer = Timer('test', 0, lambda: None)

    assert timer.start() is False
    assert not timer.running


def test_timer_survives_exception():
    """Раньше исключение в цикле убивало поток, и таймер молча переставал работать"""
    calls = []

    def target():
        calls.append(1)
        raise RuntimeError('bang')

    timer = Timer('test', 0.01, target)
    timer.start()
    sleep(0.05)
    timer.stop()

    assert len(calls) > 1, 'после исключения таймер перестал срабатывать'


def test_check_active_hides_and_restores_posts():
    client = make_client(make_token(900))
    tracker = VisibilityTracker(client)
    post = Post.from_dict(dict(POST), client=client)
    client.visibility = tracker  # посты живут в трекере клиента
    post.set_visible()

    assert tracker.posts == [post]

    tracker.last_active = datetime.now() - timedelta(seconds=client.config.dwell_inactive_timeout + 1)
    tracker.check_active()
    assert tracker.posts == [], 'пост должен скрыться, пока пользователь неактивен'

    tracker.set_active()
    tracker.check_active()
    assert tracker.posts == [post], 'и вернуться, когда он вернулся'


def test_update_stats_applies_response(monkeypatch):
    client = make_client(make_token(900))
    tracker = VisibilityTracker(client)
    post = Post.from_dict(dict(POST), client=client)
    tracker.posts.append(post)

    id = post.id
    calls = []
    monkeypatch.setattr(
        'itd.core.visibility.get_stats',
        lambda client, ids: (calls.append(ids), make_response(200, {'posts': [{'id': str(id), 'likesCount': 7}]}))[1]
    )

    tracker.update_stats()

    assert calls == [[id]]
    assert post.likes_count == 7


def test_update_stats_without_posts_does_not_request(monkeypatch):
    client = make_client(make_token(900))
    monkeypatch.setattr('itd.core.visibility.get_stats', lambda *args: pytest.fail('запрос без видимых постов'))

    VisibilityTracker(client).update_stats()


def test_client_delegates_to_tracker():
    client = make_client(make_token(900))

    assert client.visible_posts is client.visibility.posts

    client.set_active()
    assert client.last_active == client.visibility.last_active
