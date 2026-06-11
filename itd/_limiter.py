from time import monotonic, sleep


class RateLimiter:
    window: int = 65

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.requests = []

    def sync(self, remaining: int):
        used = self.capacity - remaining
        if used > 0:
            self.requests = self.requests[-used:]  # ai
        while len(self.requests) < used:
            self.requests.append(monotonic())

    def acquire(self):
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
