from time import monotonic, sleep

from itd.logger import get_logger

l = get_logger('limiter')


class RateLimiter:
    window: int = 65

    def __init__(self, capacity: int):
        l.debug(r'\[%s] create rate limiter', capacity)
        self.capacity = capacity

    def sync(self, remaining: int): ...
    def acquire(self): ...
    def on_limit(self): ...
    def get_delay(self): ...


class SafeRateLimiter(RateLimiter):
    def __init__(self, capacity: int):
        super().__init__(capacity)
        self.delay = 60 / capacity
        self.last_request = monotonic()
        self.requests = 0

    def get_delay(self):
        self.requests += 1
        self.last_request = monotonic()
        return max(0.1, self.delay - (monotonic() - self.last_request))

    def acquire(self):
        l.debug(r'\[%s] acquire limiter delay=%s', self.capacity, round(self.delay, 2))
        sleep(self.get_delay())

    def sync(self, remaining: int):
        l.info(r'\[%s] sync limiter remaining=%s', self.capacity, remaining)
        if remaining < self.capacity * 0.2:
            self.delay *= 1 + 1 / (remaining or 0.5)
            l.info(r'\[%s] increase delay=%s', self.capacity, round(self.delay, 2))
        if remaining > self.capacity * 0.95:
            self.delay *= 0.7
            l.info(r'\[%s] decrease delay=%s', self.capacity, round(self.delay, 2))
        elif 10 < self.requests < 500 and remaining > self.capacity * 0.5:
            self.delay -= 1 / self.requests
        self.delay = max(0.1, min(self.delay, 30))

    def on_limit(self):
        self.delay *= 2
        self.delay = min(self.delay, 30)


class BurstRateLimiter(RateLimiter):
    def __init__(self, capacity: int):
        super().__init__(capacity)
        self.requests = []

    def sync(self, remaining: int):
        l.debug(r'\[%s] sync limiter remaining=%s', self.capacity, remaining)

        used = self.capacity - remaining
        if used > 0:
            self.requests = self.requests[-used:]  # ai
        while len(self.requests) < used:
            self.requests.append(monotonic())

    def acquire(self):
        l.debug(r'\[%s] acquire limiter', self.capacity)

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
                sleep(self.get_delay())

    def get_delay(self):
        return max(self.requests[0] + self.window - monotonic(), 0.1)
