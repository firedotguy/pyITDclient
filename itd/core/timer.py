from __future__ import annotations

from atexit import register, unregister
from threading import Event, Thread
from typing import Callable

from itd.core.logger import get_logger

l = get_logger('timer')  # noqa: E741


class Timer:
    """Фоновый поток, дергающий `target` раз в `interval` секунд

    Args:
        name (str): Имя (для логов)
        interval (float): Интервал в секундах (0 - таймер не запустится)
        target (Callable[[], None]): Что вызывать
        on_exit (Callable[[], None] | None, optional): Что вызвать при выходе из программы. Defaults to None.
    """

    def __init__(self, name: str, interval: float, target: Callable[[], None], on_exit: Callable[[], None] | None = None) -> None:
        self.name = name
        self.interval = interval
        self.target = target
        self.on_exit = on_exit
        self._thread: Thread | None = None
        self._stopped = Event()

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self) -> bool:
        """Запустить таймер

        Returns:
            bool: Запущен ли (False, если интервал нулевой или таймер уже работает)
        """
        if not self.interval or self.running:
            return False

        l.debug('start %s timer interval=%s', self.name, self.interval)
        self._stopped.clear()
        self._thread = Thread(target=self._loop, name=f'itd-{self.name}', daemon=True)
        self._thread.start()
        register(self._on_exit)
        return True

    def stop(self, *, run_on_exit: bool = False) -> None:
        """Остановить таймер

        Args:
            run_on_exit (bool, optional): Вызвать ли `on_exit` (как при выходе из программы). Defaults to False.
        """
        if not self.running:
            return

        l.debug('stop %s timer', self.name)
        self._stopped.set()  # ждем на Event, а не sleep - поэтому просыпаемся сразу
        unregister(self._on_exit)
        if self._thread:
            self._thread.join(timeout=1)  # чтобы после stop() таймер был действительно остановлен, а не вот-вот
        if run_on_exit and self.on_exit:
            self.on_exit()

    def _loop(self) -> None:
        while not self._stopped.wait(self.interval):
            try:
                self.target()
            except Exception:  # иначе поток тихо умирает и таймер перестает работать до конца жизни клиента
                l.exception('%s timer failed', self.name)

    def _on_exit(self) -> None:
        self._stopped.set()
        if self._thread:
            self._thread.join(timeout=0)
        if self.on_exit:
            self.on_exit()
