from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from itd.api.posts import get_stats
from itd.core.logger import get_logger
from itd.core.timer import Timer
from itd.enums import ViewReason
from itd.exceptions import NotFoundError

if TYPE_CHECKING:
    from itd.core.client import Client
    from itd.models.post import Post

l = get_logger('visibility')  # noqa: E741


class VisibilityTracker:
    """Видимые посты: обновление их статистики и скрытие, пока пользователь неактивен

    Оба таймера живут здесь, а не в клиенте: клиенту от них нужен только запуск.
    """

    def __init__(self, client: Client) -> None:
        self.client = client
        self.posts: list[Post] = []
        self.last_active = datetime.now()

        self._buffer: list[Post] = []  # посты, скрытые из-за неактивности - их надо показать обратно
        self.stats_timer = Timer('post stats', client.config.post_update_stats_interval, self.update_stats)
        self.active_timer = Timer('check active', client.config.dwell_check_active_interval, self.check_active)

    def start(self) -> None:
        """Запустить таймеры, включенные конфигом"""
        if self.client.config._post_update_stats:
            self.stats_timer.start()
        if self.client.config._dwell_check_active:
            self.active_timer.start()

    def stop(self) -> None:
        self.stats_timer.stop()
        self.active_timer.stop()

    def set_active(self) -> None:
        """Отметить активность пользователя (скролл, движение мыши и тд)"""
        self.last_active = datetime.now()

    @property
    def is_active(self) -> bool:
        return self.last_active + timedelta(seconds=self.client.config.dwell_inactive_timeout) > datetime.now()

    def update_stats(self) -> None:
        """Обновить статистику видимых постов (одним запросом)"""
        if len(self.posts) == 0:
            return

        l.debug('update post stats count=%s', len(self.posts))
        stats: list[dict] = get_stats(self.client, [post.id for post in self.posts]).json().get('posts', [])
        if len(stats) != len(self.posts):
            raise NotFoundError('Post(s)')

        for post in self.posts:
            post._set_stats(next((stat for stat in stats if stat['id'] == str(post.id))))

    def check_active(self) -> None:
        """Скрыть видимые посты, если пользователь ушел, и вернуть их, когда вернулся"""
        is_active = self.is_active

        if not self._buffer and not is_active:
            l.debug('user is inactive, hide %s posts', len(self.posts))
            self._buffer = self.posts.copy()
            for post in self._buffer:
                post._entered_at = datetime.now() - timedelta(seconds=self.client.config.dwell_inactive_timeout)
                post.set_invisible(reason=ViewReason.INACTIVE)

        elif self._buffer and is_active:
            l.debug('user is back, show %s posts', len(self._buffer))
            for post in self._buffer:
                post.set_visible()
            self._buffer.clear()
