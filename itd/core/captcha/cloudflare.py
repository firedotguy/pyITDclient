# credits: @itdStatus

from time import sleep, time

from itd.core.captcha.base import BaseProvider  # , providers


class CloudflareProvider(BaseProvider):
    url = 'https://xn--d1ah4a.com/turnstile.html?theme=dark'
    _init_script = """
    () => {
        if (window.__t_patched) return;
        window.__t_patched = true;
        window.__t__ = null;

        window.onSuccess = tk => { window.__t__ = tk; };

        window.addEventListener('message', ev => {
            try {
                const data = (typeof ev.data === 'string') ? JSON.parse(ev.data) : ev.data;
                if (!data) return;
                const tk = data.token || data['cf-turnstile-response'] || data.cfToken;
                if (tk && typeof tk === 'string' && tk.length > 20) window.__t__ = tk;
            } catch (_) {}
        }, true);

        let attempts = 0;
        const iv = setInterval(() => {
            if (typeof window.turnstile !== 'undefined') {
                clearInterval(iv);
                const orig = window.turnstile.render.bind(window.turnstile);
                window.turnstile.render = (container, opts) => {
                    const cb = opts.callback;
                    opts.callback = tk => {
                        window.__t__ = tk;
                        if (typeof cb === 'function') cb(tk);
                    };
                    return orig(container, opts);
                };
            } else if (++attempts > 150) {
                clearInterval(iv);
            }
        }, 100);

        const origFetch = window.fetch;
        window.fetch = async (...args) => {
            const res = await origFetch(...args);
            try {
                const clone = res.clone();
                const text  = await clone.text();
                const json  = JSON.parse(text);
                const tk    = json.token || json['cf-turnstile-response'];
                if (tk && tk.length > 20) window.__t__ = tk;
            } catch (_) {}
            return res;
        };

        const observer = new MutationObserver(() => {
            const inp = document.querySelector(
                'input[name="cf-turnstile-response"], input[name="cf_turnstile_response"]'
            );
            if (inp && inp.value && inp.value.length > 20) window.__t__ = inp.value;
        });
        observer.observe(document.documentElement, { subtree: true, attributes: true, childList: true });
    }
    """

    def solve(self):
        sleep(5)
        self.page.mouse.move(20, 30)
        sleep(0.15)
        self.page.mouse.click(20, 30)

        start = time()
        while start + 30 > time():
            token = self.page.evaluate("""
                (() => {
                    if (window.__t__ && window.__t__.length > 20) return window.__t__;
                    const inp = document.querySelector(
                        'input[name="cf-turnstile-response"], input[name="cf_turnstile_response"], textarea[name="cf-turnstile-response"]'
                    );
                    if (inp && inp.value && inp.value.length > 20) return inp.value;
                    return null;
                })()
            """)
            if token:
                break
            sleep(0.3)

        if not token:
            raise RuntimeError('Cloudflare token timeout')

        return token


# providers['cloudflare'] = CloudflareProvider
