from typing import cast

from camoufox.sync_api import Camoufox
from playwright.sync_api import Browser, ViewportSize


class BaseProvider:
    url: str
    _init_script: str

    def __init__(self):
        self.camoufox = Camoufox(headless='virtual', geoip=True, humanize=True)
        self.browser = None
        self.context = None

    def launch(self):
        self.browser = cast(Browser, self.camoufox.__enter__())
        self.context = self.browser.new_context(
            viewport=ViewportSize(width=1920, height=1080),
            screen=ViewportSize(width=1920, height=1080)
            # locale='ru',
            # user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0'
        )
        self.context.add_init_script(self._init_script)
        self.page = self.context.new_page()
        self.page.goto(self.url, wait_until='domcontentloaded', timeout=25000)

    def solve(self): ...

    def close(self):
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        self.camoufox.__exit__(None, None, None)


providers: dict[str, type[BaseProvider]] = {}
