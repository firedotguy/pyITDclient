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


class SafeRateLimiter(RateLimiter):
    def __init__(self, name: str, capacity: int):
        super().__init__(name, capacity)
        self.refill_rate = 1.5
        self.requests = 0
        self.remainings = []

    def acquire(self):
        l.debug(r'\[%s] acquire limiter delay=%s', self.name, round(self.refill_rate, 2))
        sleep(self.refill_rate)
        self.requests += 1

    def sync(self, remaining: int):
        l.debug(r'\[%s] sync limiter remaining=%s', self.name, remaining)
        if self.requests > 50:
            return
        if self.requests == 50:
            l.info(r'\[%s] stop learning final=%s', self.name, round(self.refill_rate, 2))
            return

        self.remainings.append(remaining or -5)
        if len(self.remainings) > 5:
            if self.remainings[-5] > remaining + 2:
                value = self.refill_rate * (1 + (self.remainings[-5] - remaining) / 8)
                l.info(
                    r'\[%s] increase refill rate %s -> %s (remaining %s -> %s)',
                    self.name,
                    round(self.refill_rate, 2),
                    round(value, 2),
                    self.remainings[-5],
                    remaining
                )
                self.refill_rate = value
                self.remainings.clear()
            elif self.remainings[-5] < remaining - 2:
                value = self.refill_rate * (1 - (self.remainings[-5] - remaining) / 8)
                l.info(
                    r'\[%s] decrease refill rate %s -> %s (remaining %s -> %s)',
                    self.name,
                    round(self.refill_rate, 2),
                    round(value, 2),
                    self.remainings[-5],
                    remaining
                )
                self.refill_rate = value
                self.remainings.clear()
            else:
                l.debug(r'\[%s] refill rate is stable', self.name)


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
    max_requests: int = 100

    def __init__(self):
        self.requests = []

    def acquire(self):
        self.requests.append(monotonic())
        self.requests = [request for request in self.requests if request > monotonic() - self.window]
        while len(self.requests) >= self.max_requests:
            self.requests = [request for request in self.requests if request > monotonic() - self.window]
            if self.requests:
                sleep(max(self.requests[0] + self.window - monotonic(), 0.1))
