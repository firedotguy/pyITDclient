from time import sleep

from itd.core.captcha.base import BaseProvider, providers

SITEKEY = 'sk_44d64cf7bf8bc8377f5b'


class ItdProvider(BaseProvider):
    url = f'https://captcha.xn--d1ah4a.com/widget.html?sitekey={SITEKEY}'
    _init_script = """
    const plugins = [new Object(), new Object(), new Object(), new Object(), new Object()];
    plugins.item = (i) => plugins[i];
    Object.defineProperty(navigator, 'plugins', { get: () => plugins});
    window.Plugin = Object;

    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    Object.defineProperty(navigator, 'languages', { get: () => ['ru-RU', 'ru', 'en-US', 'en']});
    Object.defineProperty(navigator, 'platform', { get: () => 'Windows 11'});
    Object.defineProperty(navigator, 'mimeTypes', { get: () => [0, 0]});

    matchMedia = (a) => ({matches: a.includes('dark')}) ;

    const _origOwnProp = Object.getOwnPropertyDescriptor;
    Object.defineProperty(Object, 'getOwnPropertyDescriptor', { value: (o, p) => o == navigator && p == "webdriver"? undefined : _origOwnProp(o, p)});

    const _origAttach = Element.prototype.attachShadow;
    Object.defineProperty(Element.prototype, 'attachShadow', {
      configurable: true,
      writable: true,
      value: function (init) {
        const root = _origAttach.call(this, { ...init, mode: 'open' });
        (window.__roots ??= []).push({ host: this, root });
        return root;
      },
    });

    window.turnstile = null;
    const _origFetch = window.fetch;
    window.fetch = async function (u, p) {
        console.log(`invoke headers ${u}`);
        p.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        };
        const res = await _origFetch(u, p);
        if (u.includes('/api/v1/c')) {
            const json = await res.json();
            window.turnstile = json.t;
            console.log(`fetched turnstile ${window.turnstile}`);
            return new Response(JSON.stringify(json), {status: res.status, statusText: res.statusText, headers: res.headers});
        }
        return res;
    }
    """

    def solve(self):
        sleep(0.5)
        self.page.locator('#c').evaluate('(c) => c.shadowRoot.querySelector(".cb").click()')
        sleep(3)
        return self.page.evaluate('() => window.turnstile')


providers['itd'] = ItdProvider
