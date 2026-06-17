from time import monotonic, sleep

from itd.logger import get_logger

l = get_logger('limiter')


class RateLimiter:
    window: int = 65

    def __init__(self, name: str, capacity: int):
        l.debug(r'\[%s] create rate limiter limit=%s', name, capacity)
        self.name = name
        self.capacity = capacity

    def sync(self, remaining: int): ...
    def acquire(self): ...
    def on_limit(self): ...


class SafeRateLimiter(RateLimiter):
    def __init__(self, name: str, capacity: int):
        super().__init__(name, capacity)
        self.delay = 60 / capacity
        self.last_request = monotonic()

    def acquire(self):
        l.debug(r'\[%s] acquire limiter delay=%s', self.name, round(self.delay, 2))
        sleep(max(0.1, self.delay - (monotonic() - self.last_request)))
        self.last_request = monotonic()

    def sync(self, remaining: int):
        l.info(r'\[%s] sync limiter remaining=%s', self.name, remaining)
        if remaining < self.capacity * 0.1:
            self.delay *= 1 + 1 / remaining
            l.info(r'\[%s] increase delay=%s', self.name, round(self.delay, 2))
        if remaining > self.capacity * 0.9:
            self.delay *= 0.7
            l.info(r'\[%s] decrease delay=%s', self.name, round(self.delay, 2))
        self.delay = max(0.1, min(self.delay, 30))

    def on_limit(self):
        self.delay *= 2
        self.delay = min(self.delay, 30)


class BurstRateLimiter(RateLimiter):
    def __init__(self, name: str, capacity: int):
        super().__init__(name, capacity)
        self.requests = []

    def sync(self, remaining: int):
        l.debug(r'\[%s] sync limiter remaining=%s', self.name, remaining)

        used = self.capacity - remaining
        if used > 0:
            self.requests = self.requests[-used:]  # ai
        while len(self.requests) < used:
            self.requests.append(monotonic())

    def acquire(self):
        l.debug(r'\[%s] acquire limiter', self.name)

        self.requests = [request for request in self.requests if request > monotonic() - self.window]
        while len(self.requests) >= self.capacity:
            self.requests = [request for request in self.requests if request > monotonic() - self.window]
            if self.requests:
                sleep(max(self.requests[0] + self.window - monotonic(), 0.1))


class IPRateLimiter:
    window: int = 60
    max_requests: int = 90

    def __init__(self):
        self.requests = []

    def acquire(self):
        self.requests.append(monotonic())
        self.requests = [request for request in self.requests if request > monotonic() - self.window]
        while len(self.requests) >= self.max_requests:
            self.requests = [request for request in self.requests if request > monotonic() - self.window]
            if self.requests:
                sleep(max(self.requests[0] + self.window - monotonic(), 0.1))
