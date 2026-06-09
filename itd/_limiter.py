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
            sleep(self.requests[0] + self.window - monotonic())
