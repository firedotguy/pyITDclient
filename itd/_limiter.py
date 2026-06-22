from abc import ABC, abstractmethod
from time import monotonic, sleep

from itd.logger import get_logger

l = get_logger('limiter')


class RateLimiter(ABC):
    def __init__(self, capacity: int):
        l.debug(r'\[%s] create rate limiter', capacity)
        self.capacity = capacity
        self._delay = 0
        self.used = False

    @abstractmethod
    def sync(self, remaining: int): ...  # sync remaining, calls after request

    def acquire(self):  # wait, calls before request
        sleep(self.delay)

    @abstractmethod
    def on_limit(self): ...  # calls when RateLimitError raised

    def request(self):  # call before request
        self.used = True

    @property
    def delay(self):
        return self._delay


class HalfRateLimiter(RateLimiter):
    def __init__(self, capacity: int):
        super().__init__(capacity)
        self._delay = 60 / capacity
        self.last_request = 0
        self.requests = 0

    @property
    def delay(self):
        return max(0.1, self._delay - (monotonic() - self.last_request))

    def request(self):
        super().request()
        self.last_request = monotonic()
        self.requests += 1

    def sync(self, remaining: int):
        # короче тут такая задумка что лимитер оставляет половину ременинга, то есть чем ты дальше от центра тем сильнее тебя пиздит лимитер
        best = self.capacity / 2

        def diff(a, b):
            return max(a, b) - min(a, b)

        l.info(r'\[%s] sync limiter total=%s remaining=%s diff=%s', self.capacity, self.requests, remaining, diff(best, remaining))
        if remaining < best - 3 and self.requests > best:
            self._delay = min(self._delay * (1 + (diff(best, remaining) / 20)), 30)
            l.info(r'\[%s] slowdown delay=%.2f', self.capacity, self._delay)

        elif remaining > best + 3 and self.requests > best:
            self._delay = max(self._delay * (1 - (diff(best, remaining) / 50)), 0.1)
            l.info(r'\[%s] speedup delay=%.2f', self.capacity, self._delay)

    def on_limit(self):
        self._delay *= 2
        self._delay = min(self._delay, 30)


class BurstRateLimiter(RateLimiter):
    def __init__(self, capacity: int):
        super().__init__(capacity)
        self.remaining = capacity

    def sync(self, remaining: int):
        l.debug(r'\[%s] sync limiter remaining=%s', self.capacity, remaining)
        self.remaining = remaining

    @property
    def delay(self):
        if self.remaining < 3:
            return 60
        return 0

    def on_limit(self): ...


class IPRateLimiter:
    def __init__(self):
        self.requests = []

    def acquire(self):
        self.requests.append(monotonic())
        self.requests = [request for request in self.requests if request > monotonic() - 60]
        if len(self.requests) >= 90:
            sleep(max(self.requests[0] + 60 - monotonic(), 0))
