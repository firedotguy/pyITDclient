import pytest

from itd.notification import Notification, Notifications


@pytest.fixture
def notifications(client):
    n = Notifications(client)
    return n


def test_notifications_load(notifications):
    notifications.load(5)
    assert len(notifications) == 5
    for n in notifications[:4]:
        assert isinstance(n, Notification)


def test_notifications_unread_count(notifications):
    count = notifications.unread_count
    assert isinstance(count, int)
    assert count >= 0


def test_notifications_has_actor(notifications):
    for n in notifications.load(3):
        assert n.actor is not None
        assert n.actor.id is not None


def test_notification_read(notifications):
    unread = next((n for n in notifications.load(5) if not n.is_read), None)
    if unread is None:
        pytest.skip('no unread notifications to test')
    before = notifications.unread_count
    unread.read()
    assert unread.is_read
    assert notifications.unread_count == max(before - 1, 0)
