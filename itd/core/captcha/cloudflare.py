# credits: @itdStatus

from time import sleep, time

from itd.core.captcha.base import BaseProvider, providers


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


providers['cloudflare'] = CloudflareProvider
"""
"use strict";
(function (__c0, __c1) {
  "use strict";
  (function () {
    function Bn(e, t, r, n, a, u, l) {
      try {
        var d = e[u](l), f = d.value;
      } catch (s) {
        r(s);
        return;
      }
      d.done ? t(f) : Promise.resolve(f).then(n, a);
    }
    function qn(e) {
      return function () {
        var t = this, r = arguments;
        return new Promise(function (n, a) {
          var u = e.apply(t, r);
          function l(f) {
            Bn(u, n, a, l, d, "next", f);
          }
          function d(f) {
            Bn(u, n, a, l, d, "throw", f);
          }
          l(undefined);
        });
      };
    }
    function w(e, t) {
      "@swc/helpers - instanceof";
      return t != null && typeof Symbol != "undefined" && t[Symbol.hasInstance] ? !!t[Symbol.hasInstance](e) : e instanceof t;
    }
    function Ce(e) {
      for (var t = 1; t < arguments.length; t++) {
        var r = arguments[t] != null ? arguments[t] : {}, n = Object.keys(r);
        typeof Object.getOwnPropertySymbols == "function" && (n = n.concat(Object.getOwnPropertySymbols(r).filter(function (a) {
          return Object.getOwnPropertyDescriptor(r, a).enumerable;
        }))), n.forEach(function (a) {
          a in e ? Object.defineProperty(e, a, {value: r[a], enumerable: true, configurable: true, writable: true}) : e[a] = r[a], e;
        });
      }
      return e;
    }
    function Bi(e, t) {
      var r = Object.keys(e);
      if (Object.getOwnPropertySymbols) {
        var n = Object.getOwnPropertySymbols(e);
        t && (n = n.filter(function (a) {
          return Object.getOwnPropertyDescriptor(e, a).enumerable;
        })), r.push.apply(r, n);
      }
      return r;
    }
    function Tt(e, t) {
      return t = t != null ? t : {}, Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(t)) : Bi(Object(t)).forEach(function (r) {
        Object.defineProperty(e, r, Object.getOwnPropertyDescriptor(t, r));
      }), e;
    }
    function Jn(e) {
      if (Array.isArray(e)) return e;
    }
    function jn(e, t) {
      var r = e == null ? null : typeof Symbol != "undefined" && e[Symbol.iterator] || e["@@iterator"];
      if (r != null) {
        var n = [], a = true, u = false, l, d;
        try {
          for (r = r.call(e); !(a = (l = r.next()).done) && (n.push(l.value), !(t && n.length === t)); a = true) ;
        } catch (f) {
          u = true, d = f;
        } finally {
          try {
            !a && r.return != null && r.return();
          } finally {
            if (u) throw d;
          }
        }
        return n;
      }
    }
    function Kn() {
      throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
    }
    function xt(e, t) {
      (t == null || t > e.length) && (t = e.length);
      for (var r = 0, n = new Array(t); r < t; r++) n[r] = e[r];
      return n;
    }
    function Yt(e, t) {
      if (e) {
        if (typeof e == "string") return xt(e, t);
        var r = Object.prototype.toString.call(e).slice(8, -1);
        if (r === "Object" && e.constructor && (r = e.constructor.name), r === "Map" || r === "Set") return Array.from(r);
        if (r === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)) return xt(e, t);
      }
    }
    function zn(e) {
      if (Array.isArray(e)) return xt(e);
    }
    function Gn(e) {
      if (typeof Symbol != "undefined" && e[Symbol.iterator] != null || e["@@iterator"] != null) return Array.from(e);
    }
    function Xn() {
      throw new TypeError("Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
    }
    function Yn(e, t) {
      var r, n, a, u = {label: 0, sent: function () {
        if (a[0] & 1) throw a[1];
        return a[1];
      }, trys: [], ops: []}, l = Object.create((typeof Iterator == "function" ? Iterator : Object).prototype), d = Object.defineProperty;
      return d(l, "next", {value: f(0)}), d(l, "throw", {value: f(1)}), d(l, "return", {value: f(2)}), typeof Symbol == "function" && d(l, Symbol.iterator, {value: function () {
        return this;
      }}), l;
      function f(m) {
        return function (E) {
          return s([m, E]);
        };
      }
      function s(m) {
        if (r) throw new TypeError("Generator is already executing.");
        for (; l && (l = 0, m[0] && (u = 0)), u;) try {
          if (r = 1, n && (a = m[0] & 2 ? n.return : m[0] ? n.throw || ((a = n.return) && a.call(n), 0) : n.next) && !(a = a.call(n, m[1])).done) return a;
          switch (n = 0, a && (m = [m[0] & 2, a.value]), m[0]) {
            case 0:
            case 1:
              a = m;
              break;
            case 4:
              return u.label++, {value: m[1], done: false};
            case 5:
              u.label++, n = m[1], m = [0];
              continue;
            case 7:
              m = u.ops.pop(), u.trys.pop();
              continue;
            default:
              if (a = u.trys, !(a = a.length > 0 && a[a.length - 1]) && (m[0] === 6 || m[0] === 2)) {
                u = 0;
                continue;
              }
              if (m[0] === 3 && (!a || m[1] > a[0] && m[1] < a[3])) {
                u.label = m[1];
                break;
              }
              if (m[0] === 6 && u.label < a[1]) {
                u.label = a[1], a = m;
                break;
              }
              if (a && u.label < a[2]) {
                u.label = a[2], u.ops.push(m);
                break;
              }
              a[2] && u.ops.pop(), u.trys.pop();
              continue;
          }
          m = t.call(e, u);
        } catch (E) {
          m = [6, E], n = 0;
        } finally {
          r = a = 0;
        }
        if (m[0] & 5) throw m[1];
        return {value: m[0] ? m[1] : undefined, done: true};
      }
    }
    function W(e) {
      "@swc/helpers - typeof";
      return e && typeof Symbol != "undefined" && e.constructor === Symbol ? "symbol" : typeof e;
    }
    var Qt = "cf-chl-widget-", J = "cloudflare-challenge", Qn = ".cf-turnstile", $n = ".cf-challenge", Zn = ".g-recaptcha", ea = "cf-turnstile-response", ta = "g-recaptcha-response", it = 3e4, St = 18e4, ra = 1e4, na = 8e3, aa = 36e5, Dr = "private-token", ia = 300, oa = 10, ua = 200100, la = 200500, ca = 300020, $t = 300030, Zt = 300031, da = 3, sa = 500, fa = 500, ke = "", Fr = "_cftscs_", pa = 512;
    var de = function (e) {
      return e.Managed = "managed", e.NonInteractive = "non-interactive", e.Invisible = "invisible", e;
    }({}), ne = function (e) {
      return e.Normal = "normal", e.Compact = "compact", e.Invisible = "invisible", e.Flexible = "flexible", e;
    }({}), er = function (e) {
      return e.Auto = "auto", e.Light = "light", e.Dark = "dark", e;
    }({}), tr = function (e) {
      return e.Verifying = "verifying", e.VerifyingHavingTroubles = "verifying-having-troubles", e.VerifyingOverrun = "verifying-overrun", e.FailureWoHavingTroubles = "failure-wo-having-troubles", e.FailureHavingTroubles = "failure-having-troubles", e.FailureFeedback = "failure-feedback", e.FailureFeedbackCode = "failure-feedback-code", e.ExpiredNeverRefresh = "expired-never-refresh", e.ExpiredManualRefresh = "expired-manual-refresh", e.TimeoutNeverRefresh = "timeout-never-refresh", e.TimeoutManualRefresh = "timeout-manual-refresh", e.InteractivityRequired = "interactivity-required", e.UnsupportedBrowser = "unsupported-browser", e.TimeCheckCachedWarning = "time-check-cached-warning", e.InvalidDomain = "invalid-domain", e;
    }({}), rr = function (e) {
      return e.Never = "never", e.Auto = "auto", e;
    }({}), ot = function (e) {
      return e.Never = "never", e.Manual = "manual", e.Auto = "auto", e;
    }({}), It = function (e) {
      return e.Never = "never", e.Manual = "manual", e.Auto = "auto", e;
    }({}), ue = function (e) {
      return e.Always = "always", e.Execute = "execute", e.InteractionOnly = "interaction-only", e;
    }({}), wt = function (e) {
      return e.Render = "render", e.Execute = "execute", e;
    }({}), Rt = function (e) {
      return e.Execute = "execute", e;
    }({}), ae = function (e) {
      return e.New = "new", e.CrashedRetry = "crashed_retry", e.FailureRetry = "failure_retry", e.StaleExecute = "stale_execute", e.AutoExpire = "auto_expire", e.AutoTimeout = "auto_timeout", e.ManualRefresh = "manual_refresh", e.Api = "api", e.CheckDelays = "check_delays", e.UpgradeReload = "upgrade_reload", e.TimeCheckCachedWarningAux = "time_check_cached_warning_aux", e.JsCookiesMissingAux = "js_cookies_missing_aux", e.RedirectingTextOverrun = "redirecting_text_overrun", e;
    }({});
    var Ur = function (t) {
      var r = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : 3;
      return t.length > r ? t.slice(0, r) : t;
    };
    function ya(e) {
      if (!e) return "-";
      var t = function (n, a) {
        if (!n || n.tagName === "BODY") return a;
        for (var u = 1, l = n.previousElementSibling; l;) l.tagName === n.tagName && u++, l = l.previousElementSibling;
        var d = Ur(n.tagName.toLowerCase()), f = "".concat(d, "[").concat(u, "]");
        return t(n.parentElement, "/".concat(f).concat(a));
      };
      return t(e, "");
    }
    function ha(e) {
      if (!e) return "";
      var t = e.getBoundingClientRect();
      return "".concat(t.top, "|").concat(t.right);
    }
    var qi = {button: "b", checkbox: "c", email: "e", hidden: "h", number: "n", password: "p", radio: "r", select: "sl", submit: "s", text: "t", textarea: "ta"};
    function va(e) {
      return (zn(e.querySelectorAll("a")) || Gn(e.querySelectorAll("a")) || Yt(e.querySelectorAll("a")) || Xn()).filter(function (t) {
        return w(t, HTMLAnchorElement);
      });
    }
    function _a(e) {
      var t;
      if (!e) return "";
      var r = e.closest("form");
      if (!r) return "nf";
      var n = (zn(r.querySelectorAll("input, select, textarea, button")) || Gn(r.querySelectorAll("input, select, textarea, button")) || Yt(r.querySelectorAll("input, select, textarea, button")) || Xn()).filter(Ji), a = n.slice(0, 20).map(function (l) {
        var d;
        return (d = qi[l.type]) !== null && d !== undefined ? d : "-";
      }).join(""), u = ["m:".concat((t = r.getAttribute("method")) !== null && t !== undefined ? t : ""), "f:".concat(n.length), a].join("|");
      return u;
    }
    var Br = "c", qr = "cp", Jr = "ct", jr = "l", Kr = "nl", Hr = "n", zr = "r", Gr = "s", ji = "u", Xr = "up", Ki = "c", zi = "f", Wr = "n", Gi = "d", Xi = "g", ar = "n", Yi = "x", Qi = "p", $i = "b", Zi = "c", eo = "e", ir = "n", to = "s", ut = 20, ro = 512, ma = 99, Ee, no = (Ee = {}, (Br in Ee ? Object.defineProperty(Ee, Br, {value: [2071475277, 2531075807, 2087764529, 2650702126, 897792407, 1900861264, 193440998, 181887339], enumerable: true, configurable: true, writable: true}) : Ee[Br] = [2071475277, 2531075807, 2087764529, 2650702126, 897792407, 1900861264, 193440998, 181887339], Ee), (qr in Ee ? Object.defineProperty(Ee, qr, {value: [3710748438, 194507255, 2123698751, 2088097853], enumerable: true, configurable: true, writable: true}) : Ee[qr] = [3710748438, 194507255, 2123698751, 2088097853], Ee), (Jr in Ee ? Object.defineProperty(Ee, Jr, {value: [3716925445, 1236122734, 1917612522], enumerable: true, configurable: true, writable: true}) : Ee[Jr] = [3716925445, 1236122734, 1917612522], Ee), (jr in Ee ? Object.defineProperty(Ee, jr, {value: [173246534, 1422232710, 2984385681, 2172846769], enumerable: true, configurable: true, writable: true}) : Ee[jr] = [173246534, 1422232710, 2984385681, 2172846769], Ee), (Kr in Ee ? Object.defineProperty(Ee, Kr, {value: [517084052, 3937470477], enumerable: true, configurable: true, writable: true}) : Ee[Kr] = [517084052, 3937470477], Ee), (zr in Ee ? Object.defineProperty(Ee, zr, {value: [194507792, 1354128738, 1385023551], enumerable: true, configurable: true, writable: true}) : Ee[zr] = [194507792, 1354128738, 1385023551], Ee), (Gr in Ee ? Object.defineProperty(Ee, Gr, {value: [2172845875, 2984384787, 2901189036, 3027005952, 2088000679], enumerable: true, configurable: true, writable: true}) : Ee[Gr] = [2172845875, 2984384787, 2901189036, 3027005952, 2088000679], Ee), (Xr in Ee ? Object.defineProperty(Ee, Xr, {value: [1759493702, 1322218894], enumerable: true, configurable: true, writable: true}) : Ee[Xr] = [1759493702, 1322218894], Ee), Ee);
    function Ue(e) {
      var t;
      return (t = no[e]) !== null && t !== undefined ? t : [];
    }
    function ao(e) {
      for (var t = [], r = "", n = 0; n < e.length; n++) {
        var a = e.charCodeAt(n), u = a >= 97 && a <= 122 || a >= 48 && a <= 57;
        if (u) {
          r += e.charAt(n);
          continue;
        }
        r.length > 0 && (t.push(r), r = "");
      }
      r.length > 0 && t.push(r);
      for (var l = new Set, d = 0; d < t.length; d++) l.add(Yr(t[d])), d + 1 < t.length && l.add(Yr("".concat(t[d], " ").concat(t[d + 1])));
      return l;
    }
    function Ve(e, t) {
      return t.some(function (r) {
        return e.has(r);
      });
    }
    function nr(e) {
      return e > ma ? "".concat(ma, "+") : String(e);
    }
    function or(e) {
      if (w(e, HTMLSelectElement)) return "sl";
      if (w(e, HTMLTextAreaElement)) return "ta";
      if (w(e, HTMLButtonElement)) {
        var t = Yr(e.type);
        return t === 2139762449 ? "s" : t === 194507792 ? "rs" : "b";
      }
      switch (Yr(e.type)) {
        case 1516724467:
          return "b";
        case 2071469654:
          return "c";
        case 165454089:
          return "e";
        case 2087597251:
          return "f";
        case 1576159471:
          return "h";
        case 1682699846:
          return "n";
        case 1569157018:
          return "p";
        case 194663892:
          return "r";
        case 2158674347:
          return "se";
        case 2139762449:
          return "s";
        case 193421944:
          return "tel";
        case 193422222:
          return "u";
        default:
          return "t";
      }
    }
    function io(e) {
      var t = e.getAttribute("action");
      if (t === null || t === "") return eo;
      try {
        return new URL(t, window.location.href).origin === window.location.origin ? to : Zi;
      } catch (r) {
        return $i;
      }
    }
    function oo(e) {
      var t = e.getAttribute("method"), r = ((t === null || t === "" ? "get" : t) != null ? t === null || t === "" ? "get" : t : "").slice(0, ro).toLowerCase(), n = Yr(r);
      return n === 193411891 ? Xi : n === 2088097853 ? Qi : n === 1125889741 ? Gi : Yi;
    }
    function ba(e) {
      if (e === null || e === "") return "";
      try {
        return new URL(e, window.location.href).pathname;
      } catch (t) {
        return "";
      }
    }
    function Ea(e) {
      var t = [], r = true, n = false, a = undefined;
      try {
        for (var u = e.attributes[Symbol.iterator](), l; !(r = (l = u.next()).done); r = true) {
          var d = l.value;
          [2203664931, 2087944093, 2087876002, 5861160, 247325877, 3566271494].indexOf(Yr(d.name)) !== -1 && t.push((d.value != null ? d.value : "").slice(0, ro).toLowerCase());
        }
      } catch (f) {
        n = true, a = f;
      } finally {
        try {
          !r && u.return != null && u.return();
        } finally {
          if (n) throw a;
        }
      }
      return w(e, HTMLButtonElement) ? t.push((e.value != null ? e.value : "").slice(0, ro).toLowerCase(), (e.textContent != null ? e.textContent : "").slice(0, ro).toLowerCase()) : w(e, HTMLInputElement) && [1516724467, 2139762449].indexOf(Yr(e.type)) !== -1 && t.push((e.value != null ? e.value : "").slice(0, ro).toLowerCase()), t;
    }
    function uo(e, t) {
      var r = [], n = ba(e.getAttribute("action"));
      r.push((e.getAttribute("id") != null ? e.getAttribute("id") : "").slice(0, ro).toLowerCase(), (e.getAttribute("class") != null ? e.getAttribute("class") : "").slice(0, ro).toLowerCase(), (e.getAttribute("name") != null ? e.getAttribute("name") : "").slice(0, ro).toLowerCase(), (n != null ? n : "").slice(0, ro).toLowerCase());
      var a = true, u = false, l = undefined;
      try {
        for (var d = t.slice(0, ut)[Symbol.iterator](), f; !(a = (f = d.next()).done); a = true) {
          var s = f.value, m;
          (m = r).push.apply(m, zn(Ea(s)) || Gn(Ea(s)) || Yt(Ea(s)) || Xn());
        }
      } catch (I) {
        u = true, l = I;
      } finally {
        try {
          !a && d.return != null && d.return();
        } finally {
          if (u) throw l;
        }
      }
      var E = true, S = false, O = undefined;
      try {
        for (var b = (zn(e.querySelectorAll("label")) || Gn(e.querySelectorAll("label")) || Yt(e.querySelectorAll("label")) || Xn()).slice(0, ut)[Symbol.iterator](), A; !(E = (A = b.next()).done); E = true) {
          var P = A.value;
          r.push((P.textContent != null ? P.textContent : "").slice(0, ro).toLowerCase());
        }
      } catch (I) {
        S = true, O = I;
      } finally {
        try {
          !E && b.return != null && b.return();
        } finally {
          if (S) throw O;
        }
      }
      return r.join(" ");
    }
    function lo(e, t, r) {
      var n = [];
      n.push((e.getAttribute("id") != null ? e.getAttribute("id") : "").slice(0, ro).toLowerCase(), (e.getAttribute("class") != null ? e.getAttribute("class") : "").slice(0, ro).toLowerCase());
      var a = true, u = false, l = undefined;
      try {
        for (var d = t.slice(0, ut)[Symbol.iterator](), f; !(a = (f = d.next()).done); a = true) {
          var s = f.value, m;
          (m = n).push.apply(m, zn(Ea(s)) || Gn(Ea(s)) || Yt(Ea(s)) || Xn());
        }
      } catch (M) {
        u = true, l = M;
      } finally {
        try {
          !a && d.return != null && d.return();
        } finally {
          if (u) throw l;
        }
      }
      var E = true, S = false, O = undefined;
      try {
        for (var b = r.slice(0, ut)[Symbol.iterator](), A; !(E = (A = b.next()).done); E = true) {
          var P = A.value, I = ba(P.getAttribute("href"));
          n.push((P.textContent != null ? P.textContent : "").slice(0, ro).toLowerCase(), (I != null ? I : "").slice(0, ro).toLowerCase());
        }
      } catch (M) {
        S = true, O = M;
      } finally {
        try {
          !E && b.return != null && b.return();
        } finally {
          if (S) throw O;
        }
      }
      return n.join(" ");
    }
    function Ta(e, t) {
      var r = false, n = false, a = false, u = 0, l = true, d = false, f = undefined;
      try {
        for (var s = e[Symbol.iterator](), m; !(l = (m = s.next()).done); l = true) {
          var E = m.value;
          if (w(E, HTMLTextAreaElement)) {
            a = true;
            continue;
          }
          if (w(E, HTMLInputElement)) {
            var S = Yr(E.type);
            S === 165454089 ? r = true : S === 2087597251 ? n = true : S === 1569157018 && u++;
          }
        }
      } catch (I) {
        d = true, f = I;
      } finally {
        try {
          !l && s.return != null && s.return();
        } finally {
          if (d) throw f;
        }
      }
      var O = u > 0, b = ao(t), A = Ve(b, Ue(jr)), P = Ve(b, Ue(zr));
      return P && !A && (r || O) ? zr : O && u <= 1 && A ? jr : O && (u > 1 || Ve(b, Ue(Gr))) ? Gr : Ve(b, Ue(Br)) ? Br : n || Ve(b, Ue(Xr)) ? Xr : a && Ve(b, Ue(qr)) ? qr : Ve(b, Ue(Jr)) ? Jr : r && Ve(b, Ue(Kr)) ? Kr : ji;
    }
    function ga(e, t) {
      return t.filter(function (r) {
        return e.contains(r);
      });
    }
    function co(e, t, r) {
      var n = t.filter(function (l) {
        return w(l, HTMLInputElement) && l.type === "hidden";
      }).length, a = t.filter(function (l) {
        return w(l, HTMLButtonElement) || or(l) === "s";
      }).length, u = t.slice(0, ut).map(or).join(",");
      return {pac: Ta(t, lo(e, t, r)), pad: [Ki, ar, ir, nr(t.length), nr(n), nr(a), nr(r.length), u].join("|")};
    }
    function xa(e) {
      if (!e) return {pac: Hr, pad: [Wr, ar, ir, nr(0), nr(0), nr(0), nr(0), ""].join("|")};
      var t = e.closest("form");
      if (!t) {
        for (var r = [], n = e.parentElement, a = 0; n && n !== document.body && a < 5; n = n.parentElement, a++) r.push(n);
        if (r.length === 0) return {pac: Hr, pad: [Wr, ar, ir, nr(0), nr(0), nr(0), nr(0), ""].join("|")};
        var u = r[r.length - 1], l = (zn(u.querySelectorAll("input, select, textarea, button")) || Gn(u.querySelectorAll("input, select, textarea, button")) || Yt(u.querySelectorAll("input, select, textarea, button")) || Xn()).filter(Ji).filter(function (k) {
          return !e.contains(k);
        }), d = va(u).filter(function (k) {
          return !e.contains(k);
        }), f = null, s = true, m = false, E = undefined;
        try {
          for (var S = r[Symbol.iterator](), O; !(s = (O = S.next()).done); s = true) {
            var b = O.value, A = ga(b, l), P = ga(b, d);
            if (A.length > 0 || P.length > 0) {
              f = co(b, A, P);
              break;
            }
          }
        } catch (k) {
          m = true, E = k;
        } finally {
          try {
            !s && S.return != null && S.return();
          } finally {
            if (m) throw E;
          }
        }
        return f !== null ? f : {pac: Hr, pad: [Wr, ar, ir, nr(0), nr(0), nr(0), nr(0), ""].join("|")};
      }
      var I = (zn(t.querySelectorAll("input, select, textarea, button")) || Gn(t.querySelectorAll("input, select, textarea, button")) || Yt(t.querySelectorAll("input, select, textarea, button")) || Xn()).filter(Ji), M = I.filter(function (k) {
        return w(k, HTMLInputElement) && k.type === "hidden";
      }).length, C = I.filter(function (k) {
        return w(k, HTMLButtonElement) || or(k) === "s";
      }).length, j = va(t).length, U = I.slice(0, ut).map(or).join(",");
      return {pac: Ta(I, uo(t, I)), pad: [zi, oo(t), io(t), nr(I.length), nr(M), nr(C), nr(j), U].join("|")};
    }
    function so(e) {
      return w(e, Element) ? e : e.parentElement;
    }
    function Sa(e, t) {
      var r, n = t == null ? undefined : t.shouldIgnoreElement;
      if (n !== undefined) {
        var a = w(e, Element) ? [e] : [];
        (r = a).push.apply(r, zn(e.querySelectorAll("*")) || Gn(e.querySelectorAll("*")) || Yt(e.querySelectorAll("*")) || Xn());
        var u = new Set, l, d = true, f = false, s = undefined;
        try {
          for (var m = a[Symbol.iterator](), E; !(d = (E = m.next()).done); d = true) {
            var S = E.value;
            if (l !== undefined) {
              if (l.contains(S)) {
                u.add(S);
                continue;
              }
              l = undefined;
            }
            n(S) && (u.add(S), l = S);
          }
        } catch (O) {
          f = true, s = O;
        } finally {
          try {
            !d && m.return != null && m.return();
          } finally {
            if (f) throw s;
          }
        }
        return u;
      }
    }
    function Ia(e, t) {
      var r = so(e);
      return r === null || t === undefined ? false : t.has(r);
    }
    function wa(e, t) {
      var r = Sa(e, t);
      return (zn(e.querySelectorAll("*")) || Gn(e.querySelectorAll("*")) || Yt(e.querySelectorAll("*")) || Xn()).filter(function (n) {
        return !Ia(n, r);
      }).length;
    }
    function Ra(e, t, r, n) {
      for (var a = "", u = ("querySelectorAll" in e ? Sa(e, n) : undefined), l = document.createNodeIterator(e, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT), d = l.nextNode(); d !== null && a.length < r;) {
        if (!Ia(d, u)) {
          for (var f = 0, s = d; s !== null && s !== e;) f++, s = s.parentNode;
          if (f <= t) if (w(d, Element)) {
            var m = d;
            a += Ur(m.tagName.toLowerCase());
            var E = true, S = false, O = undefined;
            try {
              for (var b = m.attributes[Symbol.iterator](), A; !(E = (A = b.next()).done); E = true) {
                var P = A.value, I;
                (n == null || (I = n.shouldIgnoreAttribute) === null || I === undefined ? undefined : I.call(n, m, P)) !== true && (a += "_".concat(Ur(P.name, 2)));
              }
            } catch (M) {
              S = true, O = M;
            } finally {
              try {
                !E && b.return != null && b.return();
              } finally {
                if (S) throw O;
              }
            }
            a += ">";
          } else d.nodeType === Node.TEXT_NODE && (a += "-t");
        }
        d = l.nextNode();
      }
      return a.slice(0, r);
    }
    function Yr(e) {
      if (typeof e != "string") throw new TypeError("djb2: expected string, got ".concat(typeof e == "undefined" ? "undefined" : W(e)));
      for (var t = 5381, r = 0; r < e.length; r++) {
        var n = e.charCodeAt(r);
        t = t * 33 ^ n;
      }
      return t >>> 0;
    }
    function Qe(e) {
      return Qe = Object.setPrototypeOf ? Object.getPrototypeOf : function (r) {
        return r.__proto__ || Object.getPrototypeOf(r);
      }, Qe(e);
    }
    function Ot() {
      try {
        var e = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function () {}));
      } catch (t) {}
      return (Ot = function () {
        return !!e;
      })();
    }
    function Aa(e) {
      if (e === undefined) throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
      return e;
    }
    function Oa(e, t) {
      return t && (W(t) === "object" || typeof t == "function") ? t : Aa(e);
    }
    function ka(e, t) {
      if (!w(e, t)) throw new TypeError("Cannot call a class as a function");
    }
    function qe(e, t) {
      return qe = Object.setPrototypeOf || function (n, a) {
        return n.__proto__ = a, n;
      }, qe(e, t);
    }
    function La(e, t) {
      if (typeof t != "function" && t !== null) throw new TypeError("Super expression must either be null or a function");
      e.prototype = Object.create(t && t.prototype, {constructor: {value: e, writable: true, configurable: true}}), t && qe(e, t);
    }
    function Ct(e, t, r) {
      return Ot() ? Ct = Reflect.construct : Ct = function (a, u, l) {
        var d = [null];
        d.push.apply(d, u);
        var f = Function.bind.apply(a, d), s = new f;
        return l && qe(s, l.prototype), s;
      }, Ct.apply(null, arguments);
    }
    function ur(e) {
      var t = typeof Map == "function" ? new Map : undefined;
      return ur = function (n) {
        if (n === null || !(Function.toString.call(n).indexOf("[native code]") !== -1)) return n;
        if (typeof n != "function") throw new TypeError("Super expression must either be null or a function");
        if (typeof t != "undefined") {
          if (t.has(n)) return t.get(n);
          t.set(n, a);
        }
        return a.prototype = Object.create(n.prototype, {constructor: {value: a, enumerable: false, writable: true, configurable: true}}), qe(a, n);
      }, ur(e);
    }
    var Na = function (e) {
      "use strict";
      La(t, e);
      function t(r, n) {
        ka(this, t);
        var a;
        return a = (t = Qe(t), Oa(this, Ot() ? Reflect.construct(t, [r] || [], Qe(this).constructor) : t.apply(this, [r]))), ("code" in a ? Object.defineProperty(a, "code", {value: undefined, enumerable: true, configurable: true, writable: true}) : a.code = undefined, a), a.name = "TurnstileError", a.code = n, a;
      }
      return t;
    }(ur(Error));
    var po = RegExp("^https:\\/\\/(?:challenges(?:\\.fed)?\\.cloudflare\\.com|challenges\\.cloudflare-cn\\.com)\\/turnstile\\/v0(?:\\/.*)?\\/api\\.js", "u"), Vl = RegExp("\\/turnstile\\/v0(?:\\/.*)?\\/api\\.js", "u");
    function x(e, t) {
      var r = "[Cloudflare Turnstile] ".concat(e, ".");
      throw new Na(r, t);
    }
    function R(e) {
      console.warn("[Cloudflare Turnstile] ".concat(e));
    }
    function Pa(e, t) {
      try {
        return t();
      } catch (r) {
        try {
          R("Uncaught error in ".concat(e, ": ").concat(String(r)));
        } catch (n) {}
        return;
      }
    }
    function Le(e, t) {
      if (t !== undefined) return function () {
        for (var r = arguments.length, n = new Array(r), a = 0; a < r; a++) n[a] = arguments[a];
        Pa(e, function () {
          t.apply(undefined, zn(n) || Gn(n) || Yt(n) || Xn());
        });
      };
    }
    function Qr(e) {
      if (e !== undefined) return function (t) {
        return Pa("error-callback", function () {
          return e(t);
        }) === true;
      };
    }
    function kt(e) {
      return e.startsWith(Qt) ? e.slice(Qt.length) : null;
    }
    function lt(e, t) {
      var r = true, n = false, a = undefined;
      try {
        for (var u = Object.getOwnPropertySymbols(e)[Symbol.iterator](), l; !(r = (l = u.next()).done); r = true) {
          var d = l.value, f = Object.getOwnPropertyDescriptor(e, d), s = f === undefined ? undefined : Reflect.get(f, "value");
          if (t(s)) return s;
        }
      } catch (m) {
        n = true, a = m;
      } finally {
        try {
          !r && u.return != null && u.return();
        } finally {
          if (n) throw a;
        }
      }
    }
    function Lt() {
      var e = po, t = document.currentScript;
      if (w(t, HTMLScriptElement) && e.test(t.src)) return t;
      var r = document.querySelectorAll("script"), n = true, a = false, u = undefined;
      try {
        for (var l = r[Symbol.iterator](), d; !(n = (d = l.next()).done); n = true) {
          var f = d.value;
          if (w(f, HTMLScriptElement) && e.test(f.src)) return f;
        }
      } catch (s) {
        a = true, u = s;
      } finally {
        try {
          !n && l.return != null && l.return();
        } finally {
          if (a) throw u;
        }
      }
    }
    function Da() {
      var e = Lt();
      e === undefined && x("Could not find Turnstile valid script tag, some features may not be available", 43777);
      var t = e.src, r;
      try {
        r = new URL(t);
      } catch (u) {
        x("Could not parse Turnstile script tag URL", 43777);
      }
      var n = {loadedAsync: false, params: new URLSearchParams, src: t, url: r};
      (e.async || e.defer) && (n.loadedAsync = true);
      var a = t.split("?");
      return a.length > 1 && (n.params = new URLSearchParams(a[1])), n;
    }
    function lr(e) {
      e != null && e.iframeHost && e.iframeHost.remove();
    }
    var Mt = 1, Nt = 2, Me = 0, $e = 1, ct = 2, Je = 0, dt = 1, je = 2, Fa = Symbol();
    function cr(e, t) {
      Object.defineProperty(e, Fa, {configurable: true, enumerable: false, value: t});
    }
    function Ha(e, t) {
      var r = Object.getOwnPropertyDescriptor(e, Fa), n = r === undefined ? undefined : Reflect.get(r, "value");
      return t(n) ? n : lt(e, t);
    }
    function st(e) {
      var t = Ha(e, vo);
      if (t !== undefined) return cr(e, t), t;
      var r = [undefined, undefined, false];
      return cr(e, r), r;
    }
    function ft(e) {
      var t = Ha(e, mo);
      if (t !== undefined) return cr(e, t), t;
      var r = [undefined, undefined, false];
      return cr(e, r), r;
    }
    function Pt(e, t) {
      var r = ft(e), n = r[Je];
      return r[je] && n !== undefined && n !== "" ? n : t;
    }
    var Wa = function (e) {
      return e.Failure = "failure", e.Verifying = "verifying", e.Overrunning = "overrunning", e.TimeCheckCachedWarning = "timecheckcachedwarning", e.UnsupportedBrowser = "unsupportedbrowser", e.InvalidDomain = "invaliddomain", e.InvalidSitekey = "invalidsitekey", e.Custom = "custom", e;
    }({});
    var dr = ".";
    function ve(e, t) {
      return t.kills === undefined ? false : "".concat(dr).concat(t.kills).concat(dr).includes("".concat(dr).concat(e).concat(dr));
    }
    function pt(e) {
      try {
        return new URL(e, window.location.href).origin;
      } catch (t) {
        return;
      }
    }
    function $r(e, t, r) {
      if (r === undefined || r === "") {
        if (0) var n;
        return;
      }
      e == null || e.postMessage(t, r);
    }
    function me(e, t, r) {
      $r(e.contentWindow, t, r);
    }
    var Ua = 16, go = 1, Va = 0, Ba = 1, qa = 2, Ja = 3, ja = 4, Ka = 5, za = 6, Ga = 7;
    function yo(e, t) {
      try {
        var r = (new Error).stack;
        return typeof r != "string" ? undefined : [e, Math.max(0, Math.floor(Date.now() - t)), r, go];
      } catch (n) {
        return;
      }
    }
    function Xa(e) {
      return e[3] === undefined ? [e[0], e[1], e[2]] : [e[0], e[1], e[2], e[3]];
    }
    function vt(e) {
      var t;
      return (t = e == null ? undefined : e.slice(-Ua).map(Xa)) !== null && t !== undefined ? t : [];
    }
    function Dt(e, t) {
      if (!t) return false;
      if (e.length > 0) {
        var r = e[e.length - 1];
        if (r[0] === t[0] && r[2] === t[2]) {
          var n, a, u = ((n = r[3]) !== null && n !== undefined ? n : 1) + ((a = t[3]) !== null && a !== undefined ? a : 1);
          return u === r[3] ? false : (r[3] = u, true);
        }
      }
      for (e.push(Xa(t)); e.length > Ua;) e.shift();
      return true;
    }
    function Ft(e, t) {
      return ve("gcs", e) ? false : Dt(e.gcs, t);
    }
    function ho(e) {
      var t = vt(e.gcs);
      return t.length > 0 ? t : undefined;
    }
    function Ht(e) {
      if (!ve("gcs", e)) return ho(e);
    }
    function fr(e, t) {
      if (t.isInitialized) {
        var r = Ht(t);
        if (r) {
          var n = t.shadow.querySelector("#".concat("".concat(Qt).concat(e)));
          n && me(n, {cs: r, event: "gcs", source: J, widgetId: e}, t.iframeOrigin);
        }
      }
    }
    function Ke(e, t, r) {
      var n = Ft(t, r);
      return n && fr(e, t), n;
    }
    var $a = 12, _o = "fivs", bo = "tf", Ya = "...";
    function gr(e) {
      return e.iframeHost ? e.iframeHost : e.shadow.host === e.wrapper ? e.wrapper : x("Turnstile Initialization Error", 3606);
    }
    function vr(e) {
      if (w(e.iframeHost, HTMLDivElement) && e.iframeHost !== e.wrapper) {
        var t = e.iframeHost, r = e.mode === de.Invisible && !ve(_o, e) ? document.body : e.wrapper;
        t.parentNode !== r && r.appendChild(t);
      }
    }
    function Za(e) {
      var t = e.getBoundingClientRect();
      return {h: Math.round(t.height), w: Math.round(t.width), x: Math.round(t.left), y: Math.round(t.top)};
    }
    function To(e) {
      return e.isConnected ? Za(e).w > 0 && Za(e).h > 0 && Za(e).x + Za(e).w > 0 && Za(e).y + Za(e).h > 0 && Za(e).x < window.innerWidth && Za(e).y < window.innerHeight : false;
    }
    function ei(e) {
      var t = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : 80;
      return e.length <= t ? e : "".concat(e.slice(0, t - Ya.length)).concat(Ya);
    }
    function nn(e, t) {
      return e ? e === t.wrapper ? "wrapper" : e === t.iframeHost ? "iframe-host" : e === t.iframe ? "iframe" : e === document.body ? "body" : e === document.documentElement ? "document-element" : e === t.wrapper.parentElement ? "wrapper-parent" : e.contains(t.wrapper) || e.contains(t.iframeHost) ? "ancestor" : "other" : null;
    }
    function Qa(e) {
      var t = [];
      e.style.display === "none" && t.push("dn"), (e.style.visibility === "hidden" || e.style.visibility === "collapse") && t.push(e.style.visibility === "hidden" ? "vh" : "vc");
      var r = Number(e.style.opacity);
      return Number.isFinite(r) && r <= 0.01 && t.push("op"), e.style.contentVisibility === "hidden" && t.push("cv"), t;
    }
    function xo(e) {
      var t = [];
      return e.connected || t.push("dt"), (e.rect.w === 0 || e.rect.h === 0) && t.push("zs"), t;
    }
    function So(e) {
      if (e === "" || e === "none") return null;
      var t;
      try {
        t = new DOMMatrixReadOnly(e);
      } catch (r) {
        return null;
      }
      return t.a === 1 && t.b === 0 && t.c === 0 && t.d === 1 ? [t.e, t.f] : null;
    }
    function Io(e, t, r) {
      for (var n = e, a = 0; n && a < $a;) {
        var u = pr(n, t, r), l = So(u.style.transform);
        if (l && u.rect.w > 0 && u.rect.h > 0 && !u.inViewport && (Tt(Ce({}, u.rect), {x: u.rect.x - l[0], y: u.rect.y - l[1]}).w > 0 && Tt(Ce({}, u.rect), {x: u.rect.x - l[0], y: u.rect.y - l[1]}).h > 0 && Tt(Ce({}, u.rect), {x: u.rect.x - l[0], y: u.rect.y - l[1]}).x + Tt(Ce({}, u.rect), {x: u.rect.x - l[0], y: u.rect.y - l[1]}).w > 0 && Tt(Ce({}, u.rect), {x: u.rect.x - l[0], y: u.rect.y - l[1]}).y + Tt(Ce({}, u.rect), {x: u.rect.x - l[0], y: u.rect.y - l[1]}).h > 0 && Tt(Ce({}, u.rect), {x: u.rect.x - l[0], y: u.rect.y - l[1]}).x < window.innerWidth && Tt(Ce({}, u.rect), {x: u.rect.x - l[0], y: u.rect.y - l[1]}).y < window.innerHeight)) return mr(u, [bo]);
        n = n.parentElement, a += 1;
      }
      return null;
    }
    function ti(e, t) {
      var r, n = Za(e), a = window.getComputedStyle(e);
      return {connected: e.isConnected, element: (r = nn(e, t)) !== null && r !== undefined ? r : "unknown", inViewport: e.isConnected && (n.w > 0 && n.h > 0 && n.x + n.w > 0 && n.y + n.h > 0 && n.x < window.innerWidth && n.y < window.innerHeight), rect: n, style: {contentVisibility: a.contentVisibility, display: a.display, opacity: a.opacity, position: a.position, transform: ei(a.transform), visibility: a.visibility}};
    }
    function ri(e, t) {
      var r, n = window.getComputedStyle(e);
      return {connected: e.isConnected, element: (r = nn(e, t)) !== null && r !== undefined ? r : "unknown", inViewport: false, rect: {h: 0, w: 0, x: 0, y: 0}, style: {contentVisibility: n.contentVisibility, display: n.display, opacity: n.opacity, position: n.position, transform: ei(n.transform), visibility: n.visibility}};
    }
    function pr(e, t, r) {
      var n = r.get(e);
      if (n) return n;
      var a = ti(e, t);
      return r.set(e, a), a;
    }
    function mr(e, t) {
      return t.length === 0 ? null : {element: ai(e.element), reasons: t};
    }
    function ni(e, t, r, n) {
      var a = arguments.length > 4 && arguments[4] !== undefined ? arguments[4] : false, u = Qa(t);
      if (t.connected || u.push("dt"), u.length > 0) return mr(t, u);
      for (var l = e.parentElement, d = 0; l && d < $a;) {
        var f = n == null ? undefined : n.get(l);
        f || (f = a ? ri(l, r) : ti(l, r), n == null || n.set(l, f));
        var s = Qa(f);
        if (s.length > 0) return mr(f, s);
        l = l.parentElement, d += 1;
      }
      return null;
    }
    function Zr(e, t, r, n) {
      var a = ni(e, t, r, n);
      if (a) return a;
      if (!t.inViewport) {
        var u = Io(e, r, n);
        if (u) return u;
      }
      return mr(t, xo(t));
    }
    function wo(e) {
      return e.mode === de.Invisible ? {expectedHidden: true, reason: "mi"} : e.params.appearance === ue.InteractionOnly ? {expectedHidden: true, reason: "ai"} : e.params.appearance === ue.Execute && !e.isExecuting ? {expectedHidden: true, reason: "ae"} : {expectedHidden: false, reason: null};
    }
    function Ro(e, t) {
      return t === e.wrapper ? "wrapper" : t.isConnected ? t.parentElement === e.wrapper ? "wrapper" : t.parentElement === document.body ? "body" : "other" : "detached";
    }
    function ai(e) {
      switch (e) {
        case null:
          return "u";
        case "ancestor":
          return "a";
        case "body":
          return "b";
        case "detached":
          return "d";
        case "document-element":
          return "r";
        case "iframe":
          return "i";
        case "iframe-host":
          return "h";
        case "other":
          return "o";
        case "wrapper":
          return "w";
        case "wrapper-parent":
          return "p";
        default:
          return "u";
      }
    }
    function Ao(e) {
      switch (e) {
        case "body":
          return "b";
        case "detached":
          return "d";
        case "other":
          return "o";
        case "wrapper":
          return "w";
        default:
          return "u";
      }
    }
    function en(e, t) {
      if (!t) return null;
      var r;
      switch (e) {
        case "iframe":
          r = "i";
          break;
        case "iframeHost":
          r = "h";
          break;
        case "wrapper":
          r = "w";
          break;
        default:
          r = "u";
          break;
      }
      return "".concat(r, ":").concat(t.element, ":").concat(t.reasons.join("."));
    }
    function ii(e, t) {
      var r, n, a = gr(e), u = {iframe: t, iframeHost: a, wrapper: e.wrapper}, l = wo(e), d = Ro(e, a), f = nn(a.parentElement, u), s = {height: window.innerHeight, visibilityState: document.visibilityState, width: window.innerWidth};
      if (l.expectedHidden) {
        var m, E;
        return {appearance: (m = e.params.appearance) !== null && m !== undefined ? m : ue.Always, expectedHidden: true, expectedHiddenReason: l.reason, hostParent: f, isExecuting: e.isExecuting, mode: (E = e.mode) !== null && E !== undefined ? E : null, mount: d, reasons: [], unexpectedHidden: false, viewport: s};
      }
      var S = new Map, O = pr(e.wrapper, u, S), b = pr(a, u, S), A = pr(t, u, S), P = Zr(e.wrapper, O, u, S), I = Zr(a, b, u, S), M = Zr(t, A, u, S), C = [d === "wrapper" ? null : "m:".concat(Ao(d), ":").concat(ai(f)), en("wrapper", P), en("iframeHost", I), en("iframe", M)].filter(function (j) {
        return j !== null;
      });
      return {appearance: (r = e.params.appearance) !== null && r !== undefined ? r : ue.Always, expectedHidden: false, expectedHiddenReason: null, hostParent: f, isExecuting: e.isExecuting, mode: (n = e.mode) !== null && n !== undefined ? n : null, mount: d, reasons: zn(new Set(C)) || Gn(new Set(C)) || Yt(new Set(C)) || Xn(), unexpectedHidden: C.length > 0, viewport: s};
    }
    function Oo(e, t) {
      var r = gr(e);
      if (r.parentElement === document.body) return false;
      if (!To(t)) return true;
      var n = {iframe: t, iframeHost: r, wrapper: e.wrapper}, a = new Map, u = ri(r, n);
      return a.set(r, u), ni(r, u, n, a, true) !== null;
    }
    function oi(e, t) {
      if (e.mode !== de.Invisible || ve(_o, e)) {
        vr(e);
        return;
      }
      Oo(e, t) && vr(e);
    }
    function Co(e) {
      e.style.width = "1px", e.style.height = "1px", e.style.opacity = "0.01", e.style.position = "fixed", e.style.left = "0", e.style.top = "0", e.style.visibility = "visible", e.style.pointerEvents = "none", e.style.zIndex = "-1", e.setAttribute("tabindex", "-1"), e.setAttribute("aria-hidden", "true");
    }
    function ko(e) {
      e.style.width = "0", e.style.height = "0", e.style.opacity = "", e.style.position = "absolute", e.style.left = "", e.style.top = "", e.style.visibility = "hidden", e.style.pointerEvents = "", e.style.zIndex = "", e.setAttribute("tabindex", "-1"), e.setAttribute("aria-hidden", "true");
    }
    function an(e, t) {
      if (t.mode === undefined || ve(_o, t)) {
        ko(e);
        return;
      }
      Co(e);
    }
    var Lo = ["bg-bg", "da-dk", "de-de", "el-gr", "ja-jp", "ms-my", "ru-ru", "sk-sk", "sl-si", "sr-ba", "tl-ph", "uk-ua"], Mo = ["ar-eg", "es-es", "cs-cz", "fa-ir", "fr-fr", "hr-hr", "hu-hu", "id-id", "it-it", "lv-lv", "nb-no", "nl-nl", "pl-pl", "pt-br", "th-th", "tr-tr", "ro-ro"], ui = "https://challenges.cloudflare.com", li = [ui, "https://challenges.fed.cloudflare.com", "https://challenges.cloudflare-cn.com", "https://challenges-staging.cloudflare.com"];
    function yr(e, t, r) {
      var n, a = ui, u = (n = r == null ? undefined : r.origin) !== null && n !== undefined ? n : a;
      if (t) {
        var l;
        return (l = e["base-url"]) !== null && l !== undefined ? l : u;
      }
      return u;
    }
    function on(e, t, r, n, a, u, l, d, f, s) {
      var m = yr(r, a, d), E = s !== undefined && s !== "" ? s : u, S = E !== undefined && E !== "" ? "h/".concat(encodeURIComponent(E), "/") : "", O = f !== undefined && f !== "" ? "&".concat(f) : "", b = r["feedback-enabled"] === false ? "fbD" : "fbE", A = r.chlPageOfflabel === true ? "&offlabel=true" : "";
      return "".concat(m, "/cdn-cgi/challenge-platform/").concat(S, "turnstile/f/av0/rch").concat(n, "/").concat(e, "/").concat(t, "/").concat(r.theme, "/").concat(b, "/").concat(l, "/").concat(r.size, "?lang=").concat(r.language).concat(A).concat(O);
    }
    var un = function (t) {
      var r, n, a, u, l = window.innerWidth < 400, d = t.state !== tr.FailureFeedbackCode && (t.state === tr.FailureFeedback || t.state === tr.FailureHavingTroubles || t.errorCode === undefined || t.errorCode === 0), f = Lo.indexOf((r = (a = t.displayLanguage) === null || a === undefined ? undefined : a.toLowerCase()) !== null && r !== undefined ? r : "nonexistent") !== -1, s = Mo.indexOf((n = (u = t.displayLanguage) === null || u === undefined ? undefined : u.toLowerCase()) !== null && n !== undefined ? n : "nonexistent") !== -1;
      return l ? No({isModeratelyVerbose: s, isSmallerFeedback: d, isVerboseLanguage: f}) : d && f ? "680px" : d && s ? "670px" : d ? "650px" : f ? "690px" : "680px";
    }, No = function (t) {
      var r = t.isVerboseLanguage, n = t.isSmallerFeedback, a = t.isModeratelyVerbose;
      return n && r ? "660px" : n && a ? "620px" : n ? "600px" : r ? "770px" : a ? "740px" : "730px";
    };
    var Po = 5e3, Do = "auto-troubleshoot-click";
    function Fo(e, t) {
      var r = yr(e.params, false, t), n = Pt(e, "g"), a = n === undefined ? "" : "h/".concat(encodeURIComponent(n), "/");
      return "".concat(r, "/cdn-cgi/challenge-platform/").concat(a, "fr");
    }
    var si = function (t, r, n, a, u) {
      var l, d, f, s, m, E, S;
      if (a === undefined || a === "" || n === undefined || n === "") return false;
      var O = Fo(t, u), b = new FormData;
      b.append("consent", "on"), b.append("origin", r), b.append("issue", Do), b.append("description", ""), b.append("rayId", n), b.append("sitekey", (l = t.params.sitekey) !== null && l !== undefined ? l : ""), b.append("rcV", (d = t.rcV) !== null && d !== undefined ? d : ""), b.append("cfChlOut", (f = t.cfChlOut) !== null && f !== undefined ? f : ""), b.append("cfChlOutS", (s = t.cfChlOutS) !== null && s !== undefined ? s : ""), b.append("mode", (m = t.mode) !== null && m !== undefined ? m : ""), b.append("errorCode", String((E = t.errorCode) !== null && E !== undefined ? E : 0)), b.append("frMd", a), b.append("displayLanguage", (S = t.displayLanguage) !== null && S !== undefined ? S : "");
      try {
        if (typeof navigator != "undefined" && typeof navigator.sendBeacon == "function" && navigator.sendBeacon(O, b)) return true;
      } catch (A) {
        R("auto feedback report: sendBeacon threw synchronously, falling through to fetch (".concat(ln(A), ")"));
      }
      try {
        return fetch(O, Ce({body: b, keepalive: true, method: "POST", mode: "no-cors"}, ci())), true;
      } catch (A) {
        R("auto feedback report: keepalive fetch threw synchronously, falling through to plain fetch (".concat(ln(A), ")"));
      }
      try {
        fetch(O, Ce({body: b, method: "POST", mode: "no-cors"}, ci()));
      } catch (A) {
        R("auto feedback report: all transports failed (".concat(ln(A), ")"));
      }
      return false;
    };
    function ci() {
      return typeof AbortSignal == "undefined" || typeof AbortSignal.timeout != "function" ? {} : {signal: AbortSignal.timeout(Po)};
    }
    function ln(e) {
      return w(e, Error) ? e.message : "unknown error";
    }
    var hr = null, Wt = 0, fi = function () {
      if (Wt++, Wt === 1) {
        var t = document.querySelector('meta[http-equiv="refresh"]');
        t && (hr = t.getAttribute("content"), t.remove());
      }
    }, pi = function () {
      if (Wt > 0 && Wt--, Wt === 0 && hr !== null) {
        var t = document.createElement("meta");
        t.httpEquiv = "refresh", t.content = hr, hr = null, document.head.appendChild(t);
      }
    }, cn = Symbol(), Ho = "host-origin", mt = function (t) {
      t.feedbackPopup && !t.feedbackPopup.closed && t.feedbackPopup.close(), t.feedbackPopup = undefined, t.feedbackPopupOrigin = undefined;
    };
    function vi(e) {
      return e.endsWith("-fr") ? e : "".concat(e, "-fr");
    }
    function mi(e) {
      var t, r, n, a = (n = document.querySelector("#".concat(e))) === null || n === undefined || (r = n.parentElement) === null || r === undefined || (t = r.parentElement) === null || t === undefined ? undefined : t.parentElement;
      return w(a, HTMLDivElement) ? a : null;
    }
    function di(e) {
      if (!((typeof e == "undefined" ? "undefined" : W(e)) !== "object" || e === null)) {
        var t = Object.getOwnPropertyDescriptor(e, "cleanup"), r = t === undefined ? undefined : Reflect.get(t, "value");
        if (typeof r == "function") return function () {
          Reflect.apply(r, undefined, []);
        };
      }
    }
    function gi(e) {
      var t, r = di((t = Object.getOwnPropertyDescriptor(e, cn)) === null || t === undefined ? undefined : t.value);
      if (r) return r;
      var n = true, a = false, u = undefined;
      try {
        for (var l = Object.getOwnPropertySymbols(e)[Symbol.iterator](), d; !(n = (d = l.next()).done); n = true) {
          var f = d.value, s, m = di((s = Object.getOwnPropertyDescriptor(e, f)) === null || s === undefined ? undefined : s.value);
          if (m) return m;
        }
      } catch (E) {
        a = true, u = E;
      } finally {
        try {
          !n && l.return != null && l.return();
        } finally {
          if (a) throw u;
        }
      }
    }
    function Wo(e, t) {
      Object.defineProperty(e, cn, {configurable: true, enumerable: false, value: {cleanup: t}});
    }
    function Uo(e) {
      Reflect.deleteProperty(e, cn);
    }
    function Vo(e) {
      var t = new URL(e, window.location.href), r = new URLSearchParams(t.hash.startsWith("#") ? t.hash.slice(1) : t.hash);
      return r.set(Ho, window.location.origin), t.hash = r.toString(), t.toString();
    }
    var dn = function (t, r, n, a, u) {
      var l, d, f = vi(t), s = yr(r.params, false, a), m = Pt(r, "g"), E = m === undefined ? "" : "h/".concat(encodeURIComponent(m), "/"), S = Vo("".concat(s, "/cdn-cgi/challenge-platform/").concat(E, "fr/").concat(kt(t), "/").concat(r.displayLanguage, "/").concat((d = r.params.theme) !== null && d !== undefined ? d : r.theme, "/").concat(n));
      if (mt(r), window.top !== window.self) {
        var O = window.open(S, "_blank");
        if (O) {
          r.feedbackPopupOrigin = pt(S), r.feedbackPopup = O;
          var b = window.setInterval(function () {
            O.closed && (window.clearInterval(b), r.feedbackPopupCloseCheck = undefined, u == null || u());
          }, 500);
          r.feedbackPopupCloseCheck = b;
          return;
        }
        R("Unable to open feedback report popup, falling back to the embedded feedback overlay.");
      }
      r.wrapper.parentNode || x("Cannot initialize Widget, Element not found (#".concat(t, ")."), 3074);
      var A = mi(f);
      if (A) {
        var P;
        (P = gi(A)) === null || P === undefined || P();
      }
      var I = document.createElement("div");
      I.style.position = "fixed", I.style.zIndex = "2147483646", I.style.width = "100vw", I.style.height = "100vh", I.style.top = "0", I.style.left = "0", I.style.transformOrigin = "center center", I.style.overflowX = "hidden", I.style.overflowY = "auto", I.style.background = "rgba(0,0,0,0.4)";
      var M = document.createElement("div");
      M.className = "cf-wrapper-turnstile-feedback", M.style.display = "table-cell", M.style.verticalAlign = "middle", M.style.width = "100vw", M.style.height = "100vh";
      var C = document.createElement("div");
      C.className = "cf-turnstile-feedback", C.id = "cf-fr-id", C.style.width = "100vw", C.style.maxWidth = "500px", C.style.height = un(r), C.style.position = "relative", C.style.zIndex = "2147483647", C.style.backgroundColor = "#ffffff", C.style.borderRadius = "5px", C.style.left = "0px", C.style.top = "0px", C.style.overflow = "hidden", C.style.margin = "0px auto";
      var j = function () {
        C.style.height = un(r);
      }, U = function () {
        var B;
        Uo(I), r.feedbackIframeOrigin = undefined, window.removeEventListener("resize", j), (B = I.parentNode) === null || B === undefined || B.removeChild(I), u == null || u();
      }, k = document.createElement("iframe");
      k.id = f, k.setAttribute("src", S), k.setAttribute("title", "Turnstile feedback report"), k.setAttribute("allow", "cross-origin-isolated; fullscreen"), k.setAttribute("sandbox", "allow-same-origin allow-scripts allow-popups allow-forms"), k.setAttribute("scrolling", "yes"), k.style.borderWidth = "0px", k.style.width = "100%", k.style.height = "100%", k.style.overflow = "auto", r.feedbackIframeOrigin = pt(S);
      var D = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      D.setAttribute("tabindex", "0"), D.setAttribute("role", "button"), D.setAttribute("aria-label", "Close feedback report"), D.style.position = "absolute", D.style.width = "26px", D.style.height = "26px", D.style.zIndex = "2147483647", D.style.cursor = "pointer", r.displayRtl === true ? D.style.left = "24px" : D.style.right = "24px", D.style.top = "24px", D.setAttribute("width", "20"), D.setAttribute("height", "20"), D.addEventListener("click", function (X) {
        X.stopPropagation(), U();
      }), D.addEventListener("keydown", function (X) {
        (X.key === "Enter" || X.key === " ") && (X.preventDefault(), X.stopPropagation(), U());
      });
      var ie = document.createElementNS("http://www.w3.org/2000/svg", "ellipse");
      ie.setAttribute("ry", "12"), ie.setAttribute("rx", "12"), ie.setAttribute("cy", "12"), ie.setAttribute("cx", "12"), ie.setAttribute("fill", "none"), ie.setAttribute("stroke-width", "0"), D.appendChild(ie);
      var H = document.createElementNS("http://www.w3.org/2000/svg", "line");
      H.setAttribute("stroke-width", "1"), H.setAttribute("fill", "none"), H.setAttribute("x1", "6"), H.setAttribute("x2", "18"), H.setAttribute("y1", "18"), H.setAttribute("y2", "5");
      var K = document.createElementNS("http://www.w3.org/2000/svg", "line");
      K.setAttribute("stroke-width", "1"), K.setAttribute("fill", "none"), K.setAttribute("x1", "6"), K.setAttribute("x2", "18"), K.setAttribute("y1", "5"), K.setAttribute("y2", "18"), r.theme === er.Light ? (H.setAttribute("stroke", "#0A0A0A"), K.setAttribute("stroke", "#0A0A0A")) : (H.setAttribute("stroke", "#F2F2F2"), K.setAttribute("stroke", "#F2F2F2")), D.appendChild(H), D.appendChild(K), C.appendChild(k), C.appendChild(D), M.appendChild(C), I.appendChild(M), I.addEventListener("click", U), r.wrapper.parentNode.appendChild(I), window.addEventListener("resize", j), Wo(I, U);
    }, Ut = function (t) {
      var r, n = vi(t), a = mi(n);
      if (a) {
        var u = gi(a);
        if (u) {
          u();
          return;
        }
        R("Unable to find feedback overlay cleanup handler. Removing overlay without cleanup."), (r = a.parentNode) === null || r === undefined || r.removeChild(a);
      }
    };
    var Bo = 900, qo = 45, Jo = 50;
    function Ko(e, t, r) {
      var n = e.widgetMap.get(t);
      (n == null ? undefined : n.retryTimeout) !== undefined && (window.clearTimeout(n.retryTimeout), n.retryTimeout = undefined), lr(n), R("Cannot find Widget ".concat(r, ", consider using turnstile.remove() to clean up a widget.")), e.widgetMap.delete(t);
    }
    function zo(e) {
      e.watchCatSeq++;
      var t = [], r = true, n = false, a = undefined;
      try {
        for (var u = e.widgetMap[Symbol.iterator](), l; !(r = (l = u.next()).done); r = true) {
          var d = Jn(l.value) || jn(l.value, 2) || Yt(l.value, 2) || Kn(), f = d[0], s = d[1], m = "".concat(Qt).concat(f), E = s.shadow;
          if (!w(E, ShadowRoot) || !s.wrapper.isConnected) {
            s.watchcat.missingWidgetWarning || (s.watchcat.missingWidgetWarning = true, t.push({widgetElId: m, widgetId: f}));
            continue;
          }
          var S = E.querySelector("#".concat(m));
          if (S === null) {
            s.watchcat.missingWidgetWarning || (s.watchcat.missingWidgetWarning = true, t.push({widgetElId: m, widgetId: f}));
            continue;
          }
          if (s.watchcat.seq = e.watchCatSeq, s.watchcat.lastAckedSeq === 0 && (s.watchcat.lastAckedSeq = e.watchCatSeq), !(s.isComplete || s.isFailed || s.feedbackOpen)) {
            var O = s.watchcat.seq - 1 - qo, b = s.watchcat.lastAckedSeq < O, A = s.watchcat.seq - 1 - Jo, P = s.isOverrunning && s.watchcat.overrunBeginSeq !== 0 && s.watchcat.overrunBeginSeq < A;
            if ((s.isExecuting || !s.isInitialized || !s.isStale && !s.isExecuted) && s.watchcat.lastAckedSeq !== 0 && b || P) {
              var I, M;
              s.watchcat.lastAckedSeq = 0, s.watchcat.seq = 0, s.isExecuting = false;
              var C = function (et, Fe) {
                console.log("Turnstile Widget seem to have ".concat(et, ": "), Fe);
              };
              C(b ? "hung" : "crashed", f);
              var j = b ? $t : Zt;
              if ((M = e.internalMsgHandler) === null || M === undefined || M.call(e, {code: j, event: "fail", rcV: (I = s.nextRcV) !== null && I !== undefined ? I : ke, source: J, widgetId: f}), 0) var U;
              continue;
            }
            me(S, {event: "meow", seq: e.watchCatSeq, source: J, widgetId: f}, s.iframeOrigin);
          }
        }
      } catch (Se) {
        n = true, a = Se;
      } finally {
        try {
          !r && u.return != null && u.return();
        } finally {
          if (n) throw a;
        }
      }
      var k = true, D = false, ie = undefined;
      try {
        for (var H = t[Symbol.iterator](), K; !(k = (K = H.next()).done); k = true) {
          var X = K.value, B = X.widgetElId, xe = X.widgetId;
          Ko(e, xe, B);
        }
      } catch (Se) {
        D = true, ie = Se;
      } finally {
        try {
          !k && H.return != null && H.return();
        } finally {
          if (D) throw ie;
        }
      }
      t.length > 0 && e.widgetMap.size === 0 && Vt(e);
    }
    function sn(e) {
      var t, r;
      (r = (t = e).watchCatInterval) !== null && r !== undefined || (t.watchCatInterval = setInterval(function () {
        zo(e);
      }, Bo));
    }
    function Vt(e) {
      var t = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : false;
      e.watchCatInterval !== null && (e.widgetMap.size === 0 || t) && (clearInterval(e.watchCatInterval), e.watchCatInterval = null);
    }
    var pn = Symbol();
    function hi(e) {
      return (typeof e == "undefined" ? "undefined" : W(e)) === "object" && e !== null ? e : undefined;
    }
    function Go(e, t) {
      Object.defineProperty(e, pn, {configurable: true, enumerable: false, value: t});
    }
    function Xo(e) {
      var t = Object.getOwnPropertyDescriptor(e, pn), r = t === undefined ? undefined : Reflect.get(t, "value");
      if ((typeof r == "undefined" ? "undefined" : W(r)) === "object" && r !== null && "widgetMap" in r && w(r.widgetMap, Map) && "upgradeAttempts" in r && typeof r.upgradeAttempts == "number" && "upgradeCompletedCount" in r && typeof r.upgradeCompletedCount == "number") return r;
      var n = lt(e, fn);
      if (n) return n;
    }
    function _i(e) {
      Reflect.deleteProperty(e, pn);
      var t = true, r = false, n = undefined;
      try {
        for (var a = Object.getOwnPropertySymbols(e)[Symbol.iterator](), u; !(t = (u = a.next()).done); t = true) {
          var l = u.value, d = Object.getOwnPropertyDescriptor(e, l), f = d === undefined ? undefined : Reflect.get(d, "value");
          (typeof f == "undefined" ? "undefined" : W(f)) === "object" && f !== null && "widgetMap" in f && w(f.widgetMap, Map) && "upgradeAttempts" in f && typeof f.upgradeAttempts == "number" && "upgradeCompletedCount" in f && typeof f.upgradeCompletedCount == "number" && Reflect.deleteProperty(e, l);
        }
      } catch (s) {
        r = true, n = s;
      } finally {
        try {
          !t && a.return != null && a.return();
        } finally {
          if (r) throw n;
        }
      }
    }
    function Yo(e) {
      return !Number.isFinite(e.apiJsReloadBackoffMs) || e.apiJsReloadBackoffMs <= 0 ? it : Math.min(e.apiJsReloadBackoffMs, St);
    }
    function Qo(e) {
      return !Number.isFinite(e.apiJsReloadNextAllowedTsMs) || e.apiJsReloadNextAllowedTsMs <= 0 ? 0 : e.apiJsReloadNextAllowedTsMs;
    }
    function yi(e, t) {
      var r = Reflect.get(e, t);
      return typeof r == "number" ? r : 0;
    }
    function bi(e, t) {
      var r = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : Lt;
      t.upgradeAttempts++;
      var n = r();
      if (!(n != null && n.parentNode)) return false;
      var a = hi(e);
      if (!a) return false;
      var u = n.nonce;
      Go(a, t);
      var l = new URL(n.src), d = document.createElement("script");
      l.searchParams.set("_upgrade", "true"), l.searchParams.set("_cb", String(Date.now())), d.async = true, u && (d.nonce = u), d.setAttribute("crossorigin", "anonymous"), d.src = l.toString();
      try {
        return n.parentNode.replaceChild(d, n), true;
      } catch (f) {
        if (!w(f, DOMException)) throw f;
        return _i(a), false;
      }
    }
    function Ei(e, t, r) {
      var n = hi(e);
      if (!n) return false;
      var a = Xo(n);
      if (!a) return false;
      var u = a.apiJsMismatchReloadPending;
      t.isReady = a.isReady, t.isRecaptchaCompatibilityMode = a.isRecaptchaCompatibilityMode, t.gcs = vt(a.gcs), t.lastWidgetIdx = a.lastWidgetIdx, t.scriptWasLoadedAsync = a.scriptWasLoadedAsync, t.apiJsReloadBackoffMs = u ? it : Yo(a), t.apiJsReloadNextAllowedTsMs = Qo(a), t.apiJsMismatchReloadAttempts = yi(a, "apiJsMismatchReloadAttempts"), t.apiJsMismatchReloadCompletedCount = yi(a, "apiJsMismatchReloadCompletedCount") + (u ? 1 : 0), t.apiJsMismatchReloadPending = false, t.upgradeAttempts = a.upgradeAttempts, t.upgradeCompletedCount = a.upgradeCompletedCount + 1, t.turnstileLoadInitTimeTsMs = Date.now();
      var l = st(t), d = st(a), f = l[ct];
      if (!f) {
        var s, m, E, S, O, b;
        l[ct] = d[ct], (E = (s = l)[m = Me]) !== null && E !== undefined || (s[m] = d[Me]), (b = (S = l)[O = $e]) !== null && b !== undefined || (S[O] = d[$e]);
      }
      t.watchCatInterval = null, t.watchCatSeq = a.watchCatSeq, t.widgetMap = a.widgetMap;
      var A = true, P = false, I = undefined;
      try {
        for (var M = t.widgetMap.values()[Symbol.iterator](), C; !(A = (C = M.next()).done); A = true) {
          var j = C.value;
          j.gcs = vt(j.gcs);
          var U = ft(j);
          !f || U[dt] === Nt || (l[$e] === true && typeof l[Me] == "string" ? (U[Je] = l[Me], U[dt] = Mt, U[je] = true) : (U[Je] = undefined, U[dt] = undefined, U[je] = false));
        }
      } catch (k) {
        P = true, I = k;
      } finally {
        try {
          !A && M.return != null && M.return();
        } finally {
          if (P) throw I;
        }
      }
      return Vt(a, true), a.msgHandler && window.removeEventListener("message", a.msgHandler), _i(n), r(), true;
    }
    var $o = RegExp("^[0-9A-Za-z_-]{3,100}$", "u");
    var Zo = RegExp("^[a-z0-9_-]{0,32}$", "iu");
    function hn(e) {
      return e === undefined ? true : typeof e == "string" && Zo.test(e);
    }
    var eu = RegExp("^[a-z0-9_\\-=]{0,255}$", "iu");
    function _n(e) {
      return e === undefined ? true : typeof e == "string" && eu.test(e);
    }
    var tu = RegExp("^[a-z]{2,3}(?:[-_][a-z]{2})?$", "iu");
    var Hc = RegExp("^[0-9a-z_\\-.]{5,2000}$", "iu");
    function wn(e) {
      var t = new URLSearchParams;
      if (0) {
        var r;
        if (r != null && r !== "") var n;
      }
      if (e.params["offlabel-show-privacy"] !== undefined && t.set("offlabel_show_privacy", String(e.params["offlabel-show-privacy"])), e.params["offlabel-show-help"] !== undefined && t.set("offlabel_show_help", String(e.params["offlabel-show-help"])), !(t.size === 0 || t.toString() === "")) return t.toString();
    }
    function Si(e, t) {
      if (e.isResetting = false, t) {
        t(String(la));
        return;
      }
      x("Could not load challenge from challenges.cloudflare.com.", 161);
    }
    function Ii(e, t) {
      return e ? t ? true : li.indexOf(e) !== -1 : false;
    }
    function wi() {
      for (var e = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : window, t = e; t && t.top !== t && !t.location.href.startsWith("http");) t = t.top;
      return t == null ? undefined : t.location.href;
    }
    var Mi = Symbol(), ru = "Turnstile has already been rendered in this container. The render attempt was rejected.", nu = "Turnstile skipped implicit render because a widget already exists in this container.", Rn = undefined, au = function (e) {
      return e.styleSheets.length;
    };
    function Ln(e) {
      var t = Reflect.get(window, e);
      return typeof t == "function" ? function () {
        for (var r = arguments.length, n = new Array(r), a = 0; a < r; a++) n[a] = arguments[a];
        return Reflect.apply(t, window, n);
      } : undefined;
    }
    function Ri(e, t) {
      return e == null ? t : Number(e);
    }
    function ou(e) {
      var t = JSON.stringify(e);
      return JSON.parse(t);
    }
    function Oi(e) {
      if (!((typeof e == "undefined" ? "undefined" : W(e)) !== "object" || e === null)) {
        var t = Object.getOwnPropertyDescriptor(e, Mi), r = t === undefined ? undefined : Reflect.get(t, "value");
        if ((typeof r == "undefined" ? "undefined" : W(r)) === "object" && r !== null && "clearPendingApiJsReloadRequest" in r && typeof r.clearPendingApiJsReloadRequest == "function" && "rejectPendingApiJsReloadRequest" in r && typeof r.rejectPendingApiJsReloadRequest == "function" && "rearmTimedUpgrade" in r && typeof r.rearmTimedUpgrade == "function" && "reloadAfterUpgrade" in r && typeof r.reloadAfterUpgrade == "function") return r;
        var n = lt(e, Ai);
        if (n) return n;
      }
    }
    var y = {apiJsMismatchReloadAttempts: 0, apiJsMismatchReloadCompletedCount: 0, apiJsMismatchReloadPending: false, apiJsReloadBackoffMs: it, apiJsReloadNextAllowedTsMs: 0, apiVersion: 1, gcs: [], isReady: false, isRecaptchaCompatibilityMode: false, lastWidgetIdx: 0, scriptUrl: "undefined", scriptUrlParsed: undefined, scriptWasLoadedAsync: false, turnstileLoadInitTimeTsMs: Date.now(), upgradeAttempts: 0, upgradeCompletedCount: 0, watchCatInterval: null, watchCatSeq: 0, widgetMap: new Map};
    function uu() {
      if (!(__c0 === undefined || __c0.length === 0)) {
        var e = st(y);
        e[ct] = true, e[Me] = __c0, e[$e] = __c1 === true;
      }
    }
    var Jt, Rr, Or;
    function lu(e) {
      var t = true, r = false, n = undefined;
      try {
        for (var a = y.widgetMap[Symbol.iterator](), u; !(t = (u = a.next()).done); t = true) {
          var l = Jn(u.value) || jn(u.value, 2) || Yt(u.value, 2) || Kn(), d = l[0], f = l[1];
          if (f.wrapper.parentElement === e || f.wrapper !== e && f.wrapper.contains(e) || f.shadow.contains(e)) return d;
        }
      } catch (s) {
        r = true, n = s;
      } finally {
        try {
          !t && a.return != null && a.return();
        } finally {
          if (r) throw n;
        }
      }
      return null;
    }
    function _r(e) {
      if (typeof e == "string") {
        var t = kt(e);
        return t !== null && y.widgetMap.has(t) ? t : y.widgetMap.has(e) ? e : null;
      }
      return lu(e);
    }
    function cu(e) {
      return e === "implicit" ? nu : ru;
    }
    function Mn() {
      Jt !== undefined && (window.clearTimeout(Jt), Jt = undefined);
    }
    function Ni() {
      var e = true, t = false, r = undefined;
      try {
        for (var n = y.widgetMap.values()[Symbol.iterator](), a; !(e = (a = n.next()).done); e = true) {
          var u = a.value;
          if (u.chlPageData !== undefined && u.chlPageData !== "") return true;
        }
      } catch (l) {
        t = true, r = l;
      } finally {
        try {
          !e && n.return != null && n.return();
        } finally {
          if (t) throw r;
        }
      }
      return false;
    }
    function qt(e) {
      var t = y.widgetMap.get(e), r = "".concat(Qt).concat(e);
      if (t !== undefined) {
        var n = t.shadow.querySelector("#".concat(r));
        n !== null && me(n, {apiJsMismatchReloadAttempts: y.apiJsMismatchReloadAttempts, apiJsMismatchReloadCompletedCount: y.apiJsMismatchReloadCompletedCount, event: "reloadApiJsRejected", source: J, widgetId: e}, t.iframeOrigin);
      }
    }
    function Nn() {
      var e = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {}, t = e.preserveMismatchReloadPending, r = t === undefined ? false : t;
      Or = undefined, r || (y.apiJsMismatchReloadPending = false), Rr !== undefined && (window.clearTimeout(Rr), Rr = undefined);
    }
    function Pi() {
      var e = Or;
      Nn(), e !== undefined && qt(e);
    }
    function su() {
      var e = y.apiJsReloadBackoffMs, t = Number.isFinite(e) && e > 0 ? Math.min(e, St) : it, r = Math.round(t * (0.8 + Math.random() * 0.4));
      y.apiJsReloadNextAllowedTsMs = Date.now() + r, y.apiJsReloadBackoffMs = Math.min(t * 2, St);
    }
    function fu(e) {
      Nn({preserveMismatchReloadPending: true}), y.apiJsMismatchReloadPending = true, Or = e, Rr = window.setTimeout(function () {
        Pi();
      }, ra);
    }
    function Pn() {
      Mn(), !Ni() && (Jt = window.setTimeout(function () {
        Jt = undefined, Wi();
      }, aa));
    }
    function An(e, t) {
      Fi(e, t, "");
    }
    var Dn = [];
    function ki() {
      y.isReady = true;
      var e = true, t = false, r = undefined;
      try {
        for (var n = Dn[Symbol.iterator](), a; !(e = (a = n.next()).done); e = true) {
          var u = a.value;
          u();
        }
      } catch (l) {
        t = true, r = l;
      } finally {
        try {
          !e && n.return != null && n.return();
        } finally {
          if (t) throw r;
        }
      }
    }
    function Li(e, t) {
      e.onerror = function () {
        Si(t, t.cbError);
      };
    }
    function Di(e, t) {
      var r, n = (r = e.params["response-field"]) !== null && r !== undefined ? r : true, a = y.isRecaptchaCompatibilityMode, u = "".concat(t, "_response"), l = "".concat(t, "_g_response"), d = (!n || w(document.querySelector("#".concat(u)), HTMLInputElement)) && (!a || w(document.querySelector("#".concat(l)), HTMLInputElement));
      if (!(e.responseElementsBuilt && d)) {
        if (n && !w(document.querySelector("#".concat(u)), HTMLInputElement)) {
          var f, s = document.createElement("input");
          s.type = "hidden", s.name = (f = e.params["response-field-name"]) !== null && f !== undefined ? f : ea, s.id = u, e.wrapper.appendChild(s);
        }
        if (a && !w(document.querySelector("#".concat(l)), HTMLInputElement)) {
          var m = document.createElement("input");
          m.type = "hidden", m.name = ta, m.id = l, e.wrapper.appendChild(m);
        }
        e.responseElementsBuilt = true;
      }
    }
    function Fi(e, t, r) {
      Di(e, t);
      var n = document.querySelector("#".concat(t, "_response"));
      if (n !== null && w(n, HTMLInputElement) && (n.value = r), y.isRecaptchaCompatibilityMode) {
        var a = document.querySelector("#".concat(t, "_g_response"));
        a !== null && w(a, HTMLInputElement) && (a.value = r);
      }
    }
    function br(e, t) {
      var r, n = (r = t.params.size) !== null && r !== undefined ? r : ne.Normal, a = t.mode;
      switch (a) {
        case de.NonInteractive:
        case de.Managed:
          var u;
          switch (e.style.display = "", e.style.opacity = "", e.style.position = "", e.style.left = "", e.style.top = "", e.style.visibility = "", e.style.pointerEvents = "", e.style.zIndex = "", e.setAttribute("tabindex", String((u = t.params.tabindex) !== null && u !== undefined ? u : 0)), e.removeAttribute("aria-hidden"), n) {
            case ne.Compact:
              e.style.width = "150px", e.style.height = "140px";
              break;
            case ne.Invisible:
              x('Invalid value for parameter "size", expected "'.concat(ne.Compact, '", "').concat(ne.Flexible, '", or "').concat(ne.Normal, '", got "').concat(n, '"'), 2817);
            case ne.Normal:
              e.style.width = "300px", e.style.height = "65px";
              break;
            case ne.Flexible:
              e.style.width = "100%", e.style.maxWidth = "100vw", e.style.minWidth = "300px", e.style.height = "65px";
              break;
            default:
              break;
          }
          break;
        case de.Invisible:
          an(e, t);
          break;
        default:
          x('Invalid value for parameter "mode", expected "'.concat(de.NonInteractive, '", "').concat(de.Managed, '" or "').concat(de.Invisible, '", got "').concat(String(a), '"'), 2818);
      }
    }
    function On(e, t) {
      an(e, t);
    }
    function mu(e, t) {
      var r = t.get("turnstile_iframe_alt");
      r !== undefined && r !== "" && (e.title = r);
    }
    function gu(e, t) {
      var r, n;
      return (r = (n = e.wrapper.parentNode) === null || n === undefined ? undefined : n.querySelector("#".concat(t, "-fr"))) !== null && r !== undefined ? r : null;
    }
    function yu(e) {
      var t, r;
      return ((r = e.feedbackPopup) === null || r === undefined ? undefined : r.closed) === true ? (e.feedbackPopup = undefined, e.feedbackPopupOrigin = undefined, null) : (t = e.feedbackPopup) !== null && t !== undefined ? t : null;
    }
    function Ar(e, t) {
      var r, n, a = (r = (n = gu(e, t)) === null || n === undefined ? undefined : n.contentWindow) !== null && r !== undefined ? r : null;
      if (a !== null) return {targetOrigin: e.feedbackIframeOrigin, targetWindow: a};
      var u = yu(e);
      return {targetOrigin: u === null ? undefined : e.feedbackPopupOrigin, targetWindow: u};
    }
    function hu(e) {
      if ((typeof e == "undefined" ? "undefined" : W(e)) !== "object" || e === null) return false;
      var t = e;
      return t.source === J && typeof t.event == "string" && typeof t.widgetId == "string";
    }
    function Eu(e, t, r) {
      var n, a, u = (n = (a = t.shadow.querySelector("#".concat(r))) === null || a === undefined ? undefined : a.contentWindow) !== null && n !== undefined ? n : null, l = Ar(t, r).targetWindow, f = e.data.event;
      switch (f) {
        case "feedbackActivity":
        case "requestFeedbackData":
        case "closeFeedbackReportIframe":
          return l !== null && e.source === l;
        case "refreshRequest":
          return u !== null && e.source === u || e.data.reason === "feedback_refresh" && (l !== null && e.source === l);
        case "complete":
        case "fail":
        case "feedbackInit":
        case "food":
        case "init":
        case "interactiveBegin":
        case "interactiveEnd":
        case "interactiveTimeout":
        case "languageUnsupported":
        case "overrunBegin":
        case "overrunEnd":
        case "reject":
        case "reloadApiJsRequest":
        case "reloadRequest":
        case "requestExtraParams":
        case "tokenExpired":
        case "translationInit":
        case "turnstileResults":
        case "widgetStale":
          return u !== null && e.source === u;
        default:
          {
            var s = f;
            return false;
          }
      }
    }
    function Er(e, t, r) {
      return e === null ? t : ["true", "false"].indexOf(e) !== -1 ? e === "true" : (R(r(e)), t);
    }
    function Tu() {
      try {
        var e = Lt();
        if (!e) return;
        var t = e.src, r = true, n = false, a = undefined;
        try {
          for (var u = performance.getEntriesByType("resource")[Symbol.iterator](), l; !(r = (l = u.next()).done); r = true) {
            var d = l.value;
            if (w(d, PerformanceResourceTiming) && d.name.includes(t)) return d;
          }
        } catch (f) {
          n = true, a = f;
        } finally {
          try {
            !r && u.return != null && u.return();
          } finally {
            if (n) throw a;
          }
        }
      } catch (f) {
        return;
      }
    }
    var Hi = function () {
      var e = Tu(), t = new WeakMap, r = new WeakMap, n = new WeakSet, a = new WeakSet;
      function u(c) {
        var i;
        (i = r.get(c)) === null || i === undefined || i(), r.delete(c);
      }
      function l(c) {
        var i = t.get(c);
        if (!(!n.has(c) || !a.has(c) || i === undefined || c.autoFeedbackSent === true || ve("feedback-report-auto-submit", c))) {
          var v = si(c, i.feedbackOrigin, i.rayId, c.frMd, y.scriptUrlParsed);
          v && (c.autoFeedbackSent = true, u(c), n.delete(c), t.delete(c), a.delete(c));
        }
      }
      function d(c) {
        if (u(c), !(t.get(c) === undefined || c.autoFeedbackSent === true)) {
          var i = function (h) {
            h.isTrusted && (n.add(c), l(c));
          };
          window.addEventListener("keydown", i, true), window.addEventListener("mousemove", i, true), window.addEventListener("touchstart", i, true), r.set(c, function () {
            window.removeEventListener("keydown", i, true), window.removeEventListener("mousemove", i, true), window.removeEventListener("touchstart", i, true);
          });
        }
      }
      function f(c, i, v, h, p, o) {
        return qn(function () {
          var g, L, _, N, F, z, q, ge, He, se, ce, ye;
          return Yn(this, function (fe) {
            switch (fe.label) {
              case 0:
                if (L = function ($, we) {
                  var Z = y.widgetMap.get(i);
                  Z !== c || Z.isComplete || Z.isResetting || Z.response !== h || (!$ && we !== undefined && we !== "" && R(we), S(Z, v, $));
                }, _ = c.params.sitekey, N = wi(window), N === undefined || N === "") return R("Cannot determine Turnstile's embedded location, aborting clearance redemption."), S(c, v, false), [2];
                F = Pt(c, "g"), z = F === undefined ? "" : "h/".concat(encodeURIComponent(F), "/"), q = new URL(N), ge = "https", He = "", se = "".concat(ge, "://").concat(q.host, "/cdn-cgi/challenge-platform/").concat(z, "c/").concat(o).concat(He), fe.label = 1;
              case 1:
                return fe.trys.push([1, 3, , 4]), [4, fetch(se, {body: JSON.stringify({secondaryToken: p, sitekey: _}), headers: {"Content-Type": "application/json"}, method: "POST", redirect: "manual"})];
              case 2:
                return ce = fe.sent(), ce.status === 200 ? L(true) : L(false, "Cannot determine Turnstile's embedded location, aborting clearance redemption, are you running Turnstile on a Cloudflare Zone?"), [3, 4];
              case 3:
                return ye = fe.sent(), L(false, "Error contacting Turnstile, aborting clearance redemption."), [3, 4];
              case 4:
                return [2];
            }
          });
        })();
      }
      function s(c, i, v) {
        if (c.params.retry === rr.Auto || v) {
          var h;
          if (c.feedbackOpen) {
            c.pendingRetry = {crashed: v};
            return;
          }
          var p = v ? 0 : 2e3 + ((h = c.params["retry-interval"]) !== null && h !== undefined ? h : 0);
          c.retryTimeout = window.setTimeout(function () {
            var o = v ? ae.CrashedRetry : ae.FailureRetry;
            H(o, i);
          }, p);
        }
      }
      function m(c, i, v) {
        return c.params.execution === wt.Render ? true : (i === ae.CrashedRetry || i === ae.FailureRetry || i === ae.CheckDelays || i === ae.UpgradeReload) && c.params.execution === wt.Execute && v;
      }
      function E(c, i, v) {
        if (c.feedbackOpen && (c.feedbackOpen = false, u(c), n.delete(c), t.delete(c), a.delete(c), c.feedbackPopupCloseCheck !== undefined && (window.clearInterval(c.feedbackPopupCloseCheck), c.feedbackPopupCloseCheck = undefined), pi(), window.postMessage({event: "feedbackClose", source: J, widgetId: v}, "*"), c.pendingRetry)) {
          var h = c.pendingRetry.crashed;
          c.pendingRetry = undefined, s(c, i, h);
        }
      }
      function S(c, i, v) {
        var h;
        c.response === undefined && x("[Internal Error] Widget was completed but no response was given", 1362), c.isExecuting = false, c.isComplete = true, Fi(c, i, c.response), (h = c.cbSuccess) === null || h === undefined || h.call(c, c.response, v);
      }
      function O(c) {
        if (!c) return [];
        for (var i = c.attributes, v = i.length, h = new Array(v), p = 0; p < v; p++) h[p] = i[p].name;
        return h;
      }
      function b() {
        for (var c = {}, i = [], v = document.querySelectorAll("*"), h = 0; h < v.length && i.length < 50; h++) {
          var p = v[h].tagName.toLowerCase();
          p.includes("-") && !c[p] && (c[p] = true, i.push(p));
        }
        return i;
      }
      function A(c, i, v) {
        if (c.rcV = i, 0) var h;
      }
      var P = function (i) {
        var v = Reflect.get(i, "source");
        if (v === J) {
          var h = Reflect.get(i, "widgetId");
          if (!(typeof h != "string" || h === "" || !y.widgetMap.has(h))) {
            var p = "".concat(Qt).concat(h), o = y.widgetMap.get(h);
            if (o !== undefined) switch (i.event) {
              case "init":
                {
                  o.widgetInitStartTimeTsMs = Date.now(), o.kills = i.kills, ve("gcs", o) && (o.gcs.length = 0);
                  var g = o.shadow.querySelector("#".concat(p));
                  g || x("Cannot initialize Widget, Element not found (#".concat(p, ")."), 3074), o.mode = i.mode, o.nextRcV = i.nextRcV, o.mode === de.Invisible && o.params["refresh-expired"] === ot.Manual && R("refresh-expired=manual is impossible in invisible mode, consider using '".concat(ot.Auto, "' or '").concat(ot.Never, ".'")), o.mode !== de.Managed && o.params["refresh-timeout"] !== It.Auto && R("setting refresh-timeout has no effect on an invisible/non-interactive widget and will be ignored."), o.params.appearance === ue.Always || o.isExecuting && o.params.appearance === ue.Execute ? br(g, o) : On(g, o), oi(o, g);
                  var L = o.shadow.querySelector("#".concat(p));
                  L || x("Received state for an unknown widget: ".concat(i.widgetId), 3078), me(L, {event: "init", source: J, widgetId: i.widgetId}, o.iframeOrigin);
                  break;
                }
              case "translationInit":
                {
                  var _ = o.shadow.querySelector("#".concat(p));
                  w(_, HTMLElement) || x("Cannot initialize Widget, Element not found (#".concat(p, ")."), 3074);
                  var N = new Map;
                  o.displayLanguage = i.displayLanguage, o.displayRtl = i.displayRtl, Object.keys(i.translationData).forEach(function (_e) {
                    N.set(_e, i.translationData[_e]);
                  }), mu(_, N);
                  break;
                }
              case "languageUnsupported":
                {
                  R("Language ".concat(o.params.language, " is not supported, falling back to: ").concat(i.fallback, ".")), o.displayLanguage = i.fallback;
                  break;
                }
              case "reject":
                {
                  var F = o.shadow.querySelector("#".concat(p));
                  o.isExecuting = false, w(F, HTMLElement) || x("Cannot initialize Widget, Element not found (#".concat(p, ")."), 3075);
                  var z = Reflect.get(i, "reason");
                  if (z === "unsupported_browser") {
                    var q;
                    (q = o.cbUnsupported) === null || q === undefined || q.call(o);
                  }
                  break;
                }
              case "food":
                {
                  i.seq > o.watchcat.lastAckedSeq && (o.watchcat.lastAckedSeq = i.seq);
                  break;
                }
              case "overrunBegin":
                {
                  o.isOverrunning = true, o.watchcat.overrunBeginSeq = o.watchcat.lastAckedSeq;
                  break;
                }
              case "overrunEnd":
                {
                  o.isOverrunning = false;
                  break;
                }
              case "complete":
                {
                  if (A(o, ke, i.widgetId), o.response = i.token, i.aC !== undefined && i.aC !== "") {
                    var ge;
                    (ge = o.assetCtxCallback) === null || ge === undefined || ge.call(o, i.aC);
                  }
                  if (i.scs !== undefined && i.scs !== "" && !ve("scs", o) && (o.scs = i.scs, o.params["session-continuity-persist"] === true && !ve("scs_persist", o))) {
                    var He = o.params.sitekey;
                    if (He !== null && He !== "") {
                      var se = "".concat(Fr).concat(He);
                      try {
                        localStorage.setItem(se, i.scs);
                      } catch (_e) {}
                    }
                  }
                  i.sToken !== undefined && i.sToken !== "" ? f(o, i.widgetId, p, i.token, i.sToken, i.chlId) : S(o, p, false);
                  break;
                }
              case "fail":
                {
                  var ce = Reflect.get(i, "rcV");
                  if (typeof ce == "string" && ce !== "" && A(o, ce, h), i.cfChlOut !== undefined && i.cfChlOut !== "" && (o.cfChlOut = i.cfChlOut), i.cfChlOutS !== undefined && i.cfChlOutS !== "" && (o.cfChlOutS = i.cfChlOutS), i.code !== undefined && i.code !== 0 && (o.errorCode = i.code), i.aC !== undefined && i.aC !== "") {
                    var ye;
                    (ye = o.assetCtxCallback) === null || ye === undefined || ye.call(o, i.aC);
                  }
                  o.isExecuting = false, o.isFailed = true, o.isInitialized = true, i.frMd !== undefined && i.frMd !== "" && (o.frMd = i.frMd), An(o, p);
                  var fe = o.cbError, Ie = i.code === $t || i.code === Zt, $ = i.code !== ua;
                  if (Ie) {
                    var we = o.shadow.querySelector("#".concat(p));
                    we && me(we, {event: "forceFail", source: J, widgetId: i.widgetId}, o.iframeOrigin);
                  }
                  if (fe !== undefined) {
                    var Z;
                    fe(String((Z = i.code) !== null && Z !== undefined ? Z : ca)) === true ? $ && o.params.retry === rr.Auto && !o.isResetting && s(o, p, Ie) : (i.code !== undefined && i.code !== 0 && R("Error: ".concat(i.code, ".")), $ && s(o, p, Ie));
                  } else i.code !== undefined && i.code !== 0 ? ($ && s(o, p, Ie), x("Error: ".concat(i.code), 3076)) : s(o, p, false);
                  break;
                }
              case "feedbackInit":
                {
                  i.cfChlOut !== undefined && i.cfChlOut !== "" && (o.cfChlOut = i.cfChlOut), i.cfChlOutS !== undefined && i.cfChlOutS !== "" && (o.cfChlOutS = i.cfChlOutS);
                  var Re = Ar(o, p).targetWindow;
                  if (Re) {
                    R("A feedback report form is already opened for this widget.");
                    return;
                  }
                  if (o.autoFeedbackSent !== true && !ve("feedback-report-auto-submit", o) ? t.set(o, {feedbackOrigin: i.feedbackOrigin, rayId: i.rayId}) : t.delete(o), o.feedbackOpen = true, o.retryTimeout !== undefined) {
                    var yt, rt;
                    clearTimeout(o.retryTimeout), o.retryTimeout = undefined, (rt = (yt = o).pendingRetry) !== null && rt !== undefined || (yt.pendingRetry = {crashed: false});
                  }
                  fi(), window.postMessage({event: "feedbackOpen", source: J, widgetId: i.widgetId}, "*"), dn(p, o, i.feedbackOrigin, y.scriptUrlParsed, function () {
                    E(o, p, i.widgetId);
                  });
                  break;
                }
              case "feedbackActivity":
                {
                  n.add(o), l(o);
                  break;
                }
              case "requestFeedbackData":
                {
                  a.add(o), d(o);
                  var T = o.shadow.querySelector("#".concat(p));
                  w(T, HTMLElement) || x("Received state for an unknown widget: #".concat(p, " / ").concat(i.widgetId), 3078), me(T, {event: "requestTurnstileResults", source: J, widgetId: i.widgetId}, o.iframeOrigin), l(o);
                  break;
                }
              case "turnstileResults":
                {
                  var ze, Ge, ht, Ae = Ar(o, p), Cr = Ae.targetOrigin, jt = Ae.targetWindow;
                  if (!jt) break;
                  $r(jt, {cfChlOut: (ze = o.cfChlOut) !== null && ze !== undefined ? ze : i.cfChlOut, cfChlOutS: (Ge = o.cfChlOutS) !== null && Ge !== undefined ? Ge : i.cfChlOutS, errorCode: o.errorCode, event: "feedbackData", frMd: (ht = o.frMd) !== null && ht !== undefined ? ht : i.frMd, mode: i.mode, rayId: i.rayId, rcV: i.rcV, sitekey: i.sitekey, source: J, widgetId: i.widgetId}, Cr);
                  break;
                }
              case "closeFeedbackReportIframe":
                {
                  var kr = Ar(o, p).targetWindow;
                  kr || x("Received state for an unknown widget: ".concat(i.widgetId), 3078), Ut("".concat(p, "-fr")), mt(o), E(o, p, i.widgetId);
                  break;
                }
              case "tokenExpired":
                {
                  var _t, Lr = i.token;
                  o.isExpired = true, (_t = o.cbExpired) === null || _t === undefined || _t.call(o, Lr), o.params["refresh-expired"] === ot.Auto && !o.isResetting && H(ae.AutoExpire, p);
                  break;
                }
              case "interactiveTimeout":
                {
                  A(o, ke, i.widgetId), An(o, p);
                  var Kt = o.cbTimeout;
                  if (Kt ? Kt() : o.params["refresh-timeout"] === It.Never && !o.isResetting && R("The widget encountered an interactive timeout and is set to never refresh. Consider defining a timeout handler and resetting the widget upon timeout as solving a widget in a timed-out state is going to fail."), o.params["refresh-timeout"] === It.Auto && !o.isResetting) {
                    var bt = o.cbAfterInteractive;
                    bt == null || bt(), H(ae.AutoTimeout, p);
                  }
                  break;
                }
              case "refreshRequest":
                {
                  A(o, ke, i.widgetId), Ut(p), mt(o), H(ae.ManualRefresh, p);
                  break;
                }
              case "reloadRequest":
                {
                  A(o, i.nextRcV, i.widgetId), H(i.trigger === "new" || i.trigger === "crashed_retry" || i.trigger === "failure_retry" || i.trigger === "stale_execute" || i.trigger === "auto_expire" || i.trigger === "auto_timeout" || i.trigger === "manual_refresh" || i.trigger === "api" || i.trigger === "check_delays" || i.trigger === "upgrade_reload" || i.trigger === "time_check_cached_warning_aux" || i.trigger === "js_cookies_missing_aux" || i.trigger === "redirecting_text_overrun" ? i.trigger : ae.Api, p);
                  break;
                }
              case "reloadApiJsRequest":
                {
                  if (ve("reload", o)) {
                    qt(i.widgetId);
                    break;
                  }
                  if (Or !== undefined) {
                    qt(i.widgetId);
                    break;
                  }
                  if (Date.now() < y.apiJsReloadNextAllowedTsMs) {
                    qt(i.widgetId);
                    break;
                  }
                  Wi() ? (y.apiJsMismatchReloadAttempts++, su(), fu(i.widgetId)) : qt(i.widgetId);
                  break;
                }
              case "interactiveBegin":
                {
                  var Oe, We = o.shadow.querySelector("#".concat(p));
                  w(We, HTMLElement) || x("Cannot layout widget, Element not found (#".concat(p, ")."), 3076), (Oe = o.cbBeforeInteractive) === null || Oe === undefined || Oe.call(o), o.params.appearance === ue.InteractionOnly && br(We, o);
                  break;
                }
              case "interactiveEnd":
                {
                  var oe;
                  (oe = o.cbAfterInteractive) === null || oe === undefined || oe.call(o);
                  break;
                }
              case "widgetStale":
                {
                  o.isStale = true;
                  break;
                }
              case "requestExtraParams":
                {
                  o.widgetParamsStartTimeTsMs = Date.now();
                  var Xe = o.shadow.querySelector("#".concat(p));
                  Xe || x("Received state for an unknown widget: ".concat(i.widgetId), 3078), o.isResetting = false;
                  var zt = {}, Gt = Date.now(), ee = ii(o, Xe), he = !(o.chlPageData !== undefined && o.chlPageData !== "") && !ve("pac", o) ? xa(o.wrapper) : undefined, Xt = {"d.cT": b(), "ht.atrs": O(document.body.parentElement), "pg.ref": document.referrer, pi: {ffp: _a(o.wrapper), ii: window.self !== window.top, lH: window.location.href, mL: document.querySelectorAll("meta").length, pac: he == null ? undefined : he.pac, pad: he == null ? undefined : he.pad, pfp: Ra(document, da, sa, Rn), sL: document.scripts.length, sR: gr(o).shadowRoot === null, ssL: au(document, Rn), t: "".concat(document.title.length, "|").concat(Yr(document.title)), tL: wa(document, Rn), vDa: ee.appearance, vDeh: ee.expectedHidden, vDhp: ee.hostParent, vDhr: ee.expectedHiddenReason, vDie: ee.isExecuting, vDmd: ee.mode, vDmt: ee.mount, vDrs: ee.reasons, vDuh: ee.unexpectedHidden, vDvp: ee.viewport, wp: ha(o.wrapper), xp: ya(o.wrapper).slice(0, fa)}, "w.iW": window.innerWidth}, pe = o.scs;
                  if ((pe === undefined || pe === "") && o.params["session-continuity-persist"] === true && !ve("scs_persist", o)) {
                    var nt = o.params.sitekey;
                    if (nt !== null && nt !== "") {
                      var Mr = "".concat(Fr).concat(nt);
                      try {
                        var Ye;
                        pe = (Ye = localStorage.getItem(Mr)) !== null && Ye !== undefined ? Ye : undefined;
                      } catch (_e) {}
                    }
                  }
                  pe !== undefined && pe !== "" && pe.length > pa && (pe = undefined), me(Xe, Ce({action: o.action, apiJsMismatchReloadAttempts: y.apiJsMismatchReloadAttempts, apiJsMismatchReloadCompletedCount: y.apiJsMismatchReloadCompletedCount, apiJsResourceTiming: e === undefined ? undefined : ou(e), appearance: o.params.appearance, au: y.scriptUrl, cData: o.cData, ch: "330e41bb475c", chlPageData: o.chlPageData, cs: Ht(o), event: "extraParams", execution: o.params.execution, "expiry-interval": o.params["expiry-interval"], language: o.params.language, rcV: o.rcV, "refresh-expired": o.params["refresh-expired"], "refresh-timeout": o.params["refresh-timeout"], retry: o.params.retry, "retry-interval": o.params["retry-interval"], scs: pe, source: J, timeExtraParamsMs: Date.now() - o.widgetRenderStartTimeTsMs, timeInitMs: o.widgetInitStartTimeTsMs - o.widgetRenderEndTimeTsMs, timeLoadInitMs: Date.now() - y.turnstileLoadInitTimeTsMs, timeParamsMs: o.widgetParamsStartTimeTsMs - o.widgetInitStartTimeTsMs, timeRenderMs: o.widgetRenderEndTimeTsMs - o.widgetRenderStartTimeTsMs, timeTiefMs: Date.now() - Gt, upgradeAttempts: y.upgradeAttempts, upgradeCompletedCount: y.upgradeCompletedCount, url: wi(window), wPr: Xt, widgetId: i.widgetId}, zt), o.iframeOrigin), j(o, i.widgetId, Xe), o.isInitialized = true;
                  break;
                }
              default:
                break;
            }
          }
        }
      }, I = function (i) {
        if (i.isTrusted && hu(i.data)) {
          var v = i.data;
          if (!Ii(i.origin, false)) {
            R("Ignored message from wrong origin: ".concat(i.origin, "."));
            return;
          }
          if (!(v.widgetId === "" || !y.widgetMap.has(v.widgetId))) {
            var h = "".concat(Qt).concat(v.widgetId), p = y.widgetMap.get(v.widgetId);
            if (p !== undefined) {
              if (!Eu(i, p, h)) {
                R("Ignored message from unexpected source for event: ".concat(v.event, "."));
                return;
              }
              P(v);
            }
          }
        }
      };
      y.msgHandler = I, y.internalMsgHandler = P, window.addEventListener("message", I);
      function M() {
        var c = "abcdefghijklmnopqrstuvwxyz0123456789", i = c.length, v;
        do {
          v = "";
          for (var h = 0; h < 5; h++) v += c.charAt(Math.floor(Math.random() * i));
        } while (y.widgetMap.has(v));
        return v;
      }
      function C(c) {
        var i;
        if (typeof c == "string") {
          var v = _r(c);
          if (v !== null) return v;
          try {
            var h = document.querySelector(c);
            return h === null ? null : C(h);
          } catch (o) {
            return null;
          }
        }
        if (w(c, Element)) return _r(c);
        var p = !!c;
        return p || y.widgetMap.size === 0 ? null : (i = Fe()) !== null && i !== undefined ? i : null;
      }
      function j(c, i, v) {
        for (; c.msgQueue.length > 0;) {
          var h = c.msgQueue.pop();
          me(v, {cs: h === Rt.Execute ? Ht(c) : undefined, event: h, source: J, widgetId: i}, c.iframeOrigin);
        }
      }
      function U(c) {
        return c.isExecuting;
      }
      function k(c, i) {
        if (i) {
          var v = ["retry-interval", "retry", "size", "theme", "tabindex", "execution", "refresh-expired", "refresh-timeout", "response-field-name", "response-field", "language", "base-url", "appearance", "sitekey", "feedback-enabled", "_tcsrp"], h = [], p = true, o = false, g = undefined;
          try {
            for (var L = v[Symbol.iterator](), _; !(p = (_ = L.next()).done); p = true) {
              var N = _.value;
              Object.getOwnPropertyDescriptor(i, N) !== undefined && i[N] !== undefined && i[N] !== c.params[N] && h.push(N);
            }
          } catch (F) {
            o = true, g = F;
          } finally {
            try {
              !p && L.return != null && L.return();
            } finally {
              if (o) throw g;
            }
          }
          h.length > 0 && x("The parameters ".concat(v.join(","), " is/are not allowed be changed between the calls of render() and execute() of a widget.\n    Consider rendering a new widget if you want to change the following parameters ").concat(h.join(",")), 3618), i.action !== undefined && i.action !== "" && (hn(i.action) || x('Invalid input for optional parameter "action", got "'.concat(i.action, '"'), 3604), c.action = i.action), i.cData !== undefined && i.cData !== "" && (_n(i.cData) || x('Invalid input for optional parameter "cData", got "'.concat(i.cData, '"'), 3605), c.cData = i.cData), i["after-interactive-callback"] !== undefined && (c.cbAfterInteractive = Le("after-interactive-callback", i["after-interactive-callback"])), i["before-interactive-callback"] !== undefined && (c.cbBeforeInteractive = Le("before-interactive-callback", i["before-interactive-callback"])), i.callback !== undefined && (c.cbSuccess = i.callback), i["expired-callback"] !== undefined && (c.cbExpired = Le("expired-callback", i["expired-callback"])), i["timeout-callback"] !== undefined && (c.cbTimeout = Le("timeout-callback", i["timeout-callback"])), i["error-callback"] !== undefined && (c.cbError = Qr(i["error-callback"])), i["unsupported-callback"] !== undefined && (c.cbUnsupported = i["unsupported-callback"]), i.chlPageData !== undefined && i.chlPageData !== "" && (c.chlPageData = i.chlPageData);
        }
      }
      function D(c, i, v) {
        c === "explicit" && i !== undefined && k(i, v), R(cu(c));
      }
      function ie(c) {
        H(ae.Api, c, yo(qa, y.turnstileLoadInitTimeTsMs));
      }
      function H(c, i, v) {
        var h, p, o = C(i);
        o === null && x("Nothing to reset found for provided container", 3329);
        var g = y.widgetMap.get(o);
        g === undefined && x("Widget ".concat(o, " to reset was not found."), 3331), Ft(g, v);
        var L = g.isExecuted;
        g.isResetting = true, g.response = undefined, g.mode = undefined, g.msgQueue = [], g.isComplete = false, g.isExecuted = false, g.isExecuting = false, g.isExpired = false, g.isFailed = false, g.isInitialized = false, g.isStale = false, g.isOverrunning = false, g.cfChlOut = undefined, g.cfChlOutS = undefined, g.errorCode = undefined, g.frMd = undefined, g.autoFeedbackSent = false, u(g), n.delete(g), t.delete(g), a.delete(g), g.watchcat.overrunBeginSeq = 0, g.watchcat.lastAckedSeq = 0, g.watchcat.seq = 0, m(g, c, L) && (g.msgQueue.push(Rt.Execute), g.isExecuted = true, g.isExecuting = true);
        var _ = "".concat(Qt).concat(o), N = g.shadow.querySelector("#".concat(_));
        N === null && x("Widget ".concat(o, " to reset was not found."), 3330), (g.params.appearance === ue.InteractionOnly || g.params.appearance === ue.Execute) && On(N, g), g.params.sitekey === null && x("Unexpected Error: Sitekey is null", 3347);
        var F = N.cloneNode();
        w(F, HTMLIFrameElement) || x("Unexpected Error: Cloned widget is not an iframe", 3348);
        var z = ft(g), q = on(o, g.params.sitekey, g.params, (h = g.rcV) !== null && h !== undefined ? h : ke, false, "g", c, y.scriptUrlParsed, wn(g), z[je] ? z[Je] : undefined);
        F.src = q, Li(F, g), g.iframeOrigin = pt(q), (p = N.parentNode) === null || p === undefined || p.replaceChild(F, N), An(g, _), g.retryTimeout !== undefined && window.clearTimeout(g.retryTimeout);
      }
      function K(c, i) {
        var v = "".concat(Qt).concat(c), h = ["input#".concat(v, "_response"), "input#".concat(v, "_g_response")];
        document.querySelectorAll(h.join(", ")).forEach(function (p) {
          p.remove();
        }), i.shadow.querySelectorAll(h.join(", ")).forEach(function (p) {
          p.remove();
        }), Ut(v), mt(i), i.wrapper.remove(), lr(i), i.retryTimeout !== undefined && window.clearTimeout(i.retryTimeout), y.widgetMap.delete(c), Vt(y);
      }
      function X(c) {
        var i = yo(Ja, y.turnstileLoadInitTimeTsMs), v = C(c), h = v === null ? undefined : y.widgetMap.get(v);
        if (v === null || h === undefined) {
          R("Nothing to remove found for the provided container.");
          return;
        }
        Dt(y.gcs, i), Ft(h, i), K(v, h);
      }
      function B() {
        var c = zn(y.widgetMap.keys()) || Gn(y.widgetMap.keys()) || Yt(y.widgetMap.keys()) || Xn(), i = true, v = false, h = undefined;
        try {
          for (var p = c[Symbol.iterator](), o; !(i = (o = p.next()).done); i = true) {
            var g = o.value, L = y.widgetMap.get(g), _ = "".concat(Qt).concat(g);
            L !== undefined && (Ut(_), mt(L), H(ae.UpgradeReload, _));
          }
        } catch (N) {
          v = true, h = N;
        } finally {
          try {
            !i && p.return != null && p.return();
          } finally {
            if (v) throw h;
          }
        }
      }
      function xe(c, i, v, h) {
        var p, o, g, L, _, N, F, z, q, ge, He = Date.now(), se, ce;
        if (typeof c == "string") {
          var ye = _r(c);
          if (ye === null) {
            var fe;
            try {
              fe = document.querySelector(c);
            } catch (Iu) {
              x('Invalid type for "container", expected "selector" or an implementation of "HTMLElement", got "'.concat(c, '"'), 3586);
            }
            fe === null && x('Unable to find a container for "'.concat(c, '"'), 3585), se = fe;
          } else {
            var Ie, $ = y.widgetMap.get(ye), we = (Ie = $ == null ? undefined : $.wrapper.parentElement) !== null && Ie !== undefined ? Ie : null;
            if (we !== null && (v === "explicit" && ($ == null ? undefined : $.renderSource) === "implicit")) se = we, ce = {widget: $, widgetId: ye}; else return $ !== undefined && Ke(ye, $, h), D(v, $, i), "".concat(Qt).concat(ye);
          }
        } else w(c, HTMLElement) ? se = c : x('Invalid type for parameter "container", expected "string" or an implementation of "HTMLElement"', 3587);
        if (ce === undefined) {
          var Z = _r(se);
          if (Z !== null) {
            var Re = y.widgetMap.get(Z);
            if (Re !== undefined && (v === "explicit" && (Re == null ? undefined : Re.renderSource) === "implicit") && Re.wrapper.parentElement === se) ce = {widget: Re, widgetId: Z}; else return Re && Ke(Z, Re, h), D(v, Re, i), "".concat(Qt).concat(Z);
          }
        }
        var yt = wi(window);
        if (yt === undefined || yt === "") return x("Turnstile cannot determine its page location", 3607);
        var rt = Su(se);
        if (rt !== undefined) {
          var T = Object.assign(rt, i), ze = T.action, Ge = T.cData, ht = T.chlPageData, Ae = T.sitekey;
          T.theme = (p = T.theme) !== null && p !== undefined ? p : er.Auto, T.retry = (o = T.retry) !== null && o !== undefined ? o : rr.Auto, T.execution = (g = T.execution) !== null && g !== undefined ? g : wt.Render, T.appearance = (L = T.appearance) !== null && L !== undefined ? L : ue.Always, T["retry-interval"] = Ri(T["retry-interval"], na), T["expiry-interval"] = Ri(T["expiry-interval"], (ia - oa) * 1e3), T.size = (_ = T.size) !== null && _ !== undefined ? _ : ne.Normal;
          var Cr = T.callback, jt = Le("expired-callback", T["expired-callback"]), kr = Le("timeout-callback", T["timeout-callback"]), _t = Le("after-interactive-callback", T["after-interactive-callback"]), Lr = Le("before-interactive-callback", T["before-interactive-callback"]), Kt = Qr(T["error-callback"]), bt = T["unsupported-callback"];
          typeof Ae != "string" && x('Invalid or missing type for parameter "sitekey", expected "string", got "'.concat(typeof Ae == "undefined" ? "undefined" : W(Ae), '"'), 3588), $o.test(Ae) || x('Invalid input for parameter "sitekey", got "'.concat(Ae, '"'), 3589), [ne.Normal, ne.Compact, ne.Invisible, ne.Flexible].indexOf(T.size) !== -1 || x('Invalid type for parameter "size", expected normal|compact, got "'.concat(String(T.size), '" ').concat(W(T.size)), 3590), ["auto", "dark", "light"].indexOf(T.theme) !== -1 || x('Invalid type for parameter "theme", expected dark|light|auto, got "'.concat(String(T.theme), '" ').concat(W(T.theme)), 3591), ["auto", "never"].indexOf(T.retry) !== -1 || x('Invalid type for parameter "retry", expected never|auto, got "'.concat(String(T.retry), '" ').concat(W(T.retry)), 3592), (T.language === undefined || T.language === "") && (T.language = "auto"), T.language === "auto" || tu.test(T.language) || (R('Invalid language value: "'.concat(T.language, ", expected either: auto, or an ISO 639-1 two-letter language code (e.g. en) or language and country code (e.g. en-US).")), T.language = "auto"), ["always", "execute", "interaction-only"].indexOf(T.appearance) !== -1 || x('Unknown appearance value: "'.concat(String(T.appearance), ", expected either: 'always', 'execute', or 'interaction-only'."), 3600), ["render", "execute"].indexOf(T.execution) !== -1 || x('Unknown execution value: "'.concat(String(T.execution), ", expected either: 'render' or 'execute'."), 3601), T["retry-interval"] > 0 && T["retry-interval"] < 9e5 || x('Invalid retry-interval value: "'.concat(T["retry-interval"], ', expected an integer value > 0 and < 900000"'), 3602), T["expiry-interval"] > 0 && T["expiry-interval"] < 36e4 || x('Invalid expiry-interval value: "'.concat(T["expiry-interval"], ', expected an integer value > 0 and < 360000"'), 3602);
          var Oe = (N = T["refresh-expired"]) !== null && N !== undefined ? N : ot.Auto;
          ["auto", "manual", "never"].indexOf(Oe) !== -1 ? T["refresh-expired"] = Oe : x('Invalid type for parameter "refresh-expired", expected never|manual|auto, got "'.concat(String(Oe), '" ').concat(typeof Oe == "undefined" ? "undefined" : W(Oe)), 3603);
          var We = (F = T["refresh-timeout"]) !== null && F !== undefined ? F : It.Auto;
          ["auto", "manual", "never"].indexOf(We) !== -1 ? T["refresh-timeout"] = We : x('Invalid type for parameter "refresh-timeout", expected never|manual|auto, got "'.concat(String(We), '" ').concat(typeof We == "undefined" ? "undefined" : W(We)), 3603), hn(ze) || x('Invalid input for optional parameter "action", got "'.concat(ze, '"'), 3604), _n(Ge) || x('Invalid input for optional parameter "cData", got "'.concat(Ge, '"'), 3605);
          var oe = document.createElement("iframe"), Xe = document.createElement("div"), zt = document.createElement("div"), Gt = zt.attachShadow({mode: "closed"}), ee = M(), he = "".concat(Qt).concat(ee), Xt = [], pe = T.execution === wt.Render;
          pe && Xt.push(Rt.Execute);
          var nt = vt(y.gcs);
          Dt(nt, h), y.lastWidgetIdx++;
          var Mr = {}, Ye = T._tcsrp, _e = typeof Ye == "string" && Ye.length > 0 ? Ye : undefined, Nr = st(y), Hn = _e != null ? _e : Nr[Me], Pr;
          _e !== undefined ? Pr = Nt : Nr[Me] !== undefined && (Pr = Mt);
          var Vi = _e === undefined ? Hn !== undefined && Nr[$e] === true : true, Wn = Tt(Ce({action: ze, assetCtxCallback: T._acCb, autoFeedbackSent: false, cData: Ge, cbAfterInteractive: _t, cbBeforeInteractive: Lr, cbError: Kt, cbExpired: jt, cbSuccess: Cr, cbTimeout: kr, cbUnsupported: bt, chlPageData: ht, feedbackOpen: false, gcs: nt, idx: y.lastWidgetIdx, isComplete: false, isExecuted: pe, isExecuting: pe, isExpired: false, isFailed: false, isInitialized: false, isOverrunning: false, isResetting: false, isStale: false, msgQueue: Xt, params: T, rcV: ke, renderSource: v, responseElementsBuilt: false, shadow: Gt, watchcat: {lastAckedSeq: 0, missingWidgetWarning: false, overrunBeginSeq: 0, seq: 0}}, Mr), {iframeHost: zt, widgetInitStartTimeTsMs: 0, widgetParamsStartTimeTsMs: 0, widgetRenderEndTimeTsMs: 0, widgetRenderStartTimeTsMs: He, wrapper: Xe}), Et = ft(Wn);
          Et[Je] = Hn, Et[dt] = Pr, Et[je] = Vi, y.widgetMap.set(ee, Wn), sn(y);
          var be = y.widgetMap.get(ee);
          be === undefined && x("Turnstile Initialization Error", 3606), be.chlPageData !== undefined && be.chlPageData !== "" && Mn(), oe.style.border = "none", oe.style.overflow = "hidden";
          var Un = on(ee, Ae, T, ke, false, "g", ae.New, y.scriptUrlParsed, wn(be), Et[je] ? Et[Je] : undefined);
          be.iframeOrigin = pt(Un), oe.setAttribute("src", Un), Li(oe, be);
          var Vn = ["cross-origin-isolated", "fullscreen", "autoplay", "keyboard-map", "gamepad", "xr-spatial-tracking"];
          return ((z = (ge = document.featurePolicy) === null || ge === undefined || (q = ge.features) === null || q === undefined ? undefined : q.call(ge)) !== null && z !== undefined ? z : []).indexOf(Dr) !== -1 && Vn.push(Dr), oe.setAttribute("allow", Vn.join("; ")), oe.setAttribute("sandbox", "allow-same-origin allow-scripts allow-popups"), oe.id = he, oe.title = "Widget containing a Cloudflare security challenge", Gt.appendChild(oe), On(oe, be), vr(be), Di(be, he), ce && K(ce.widgetId, ce.widget), se.appendChild(Xe), be.widgetRenderEndTimeTsMs = Date.now(), he;
        }
      }
      function et() {
        var c = [Qn, $n];
        y.isRecaptchaCompatibilityMode && c.push(Zn);
        var i = yo(Ga, y.turnstileLoadInitTimeTsMs);
        document.querySelectorAll(c.join(", ")).forEach(function (v) {
          xe(v, undefined, "implicit", i);
        });
      }
      function Fe() {
        var c, i = -1, v = true, h = false, p = undefined;
        try {
          for (var o = y.widgetMap[Symbol.iterator](), g; !(v = (g = o.next()).done); v = true) {
            var L = Jn(g.value) || jn(g.value, 2) || Yt(g.value, 2) || Kn(), _ = L[0], N = L[1];
            i < N.idx && (c = _, i = N.idx);
          }
        } catch (F) {
          h = true, p = F;
        } finally {
          try {
            !v && o.return != null && o.return();
          } finally {
            if (h) throw p;
          }
        }
        return i === -1 && x("Could not find widget", 43778), c;
      }
      var tt = {}, Ui = {showFeedback: function (i) {
        var v = C(i);
        if (v !== null) {
          var h = "".concat(Qt).concat(v), p = y.widgetMap.get(v);
          p !== undefined && dn(h, p, Wa.Custom, y.scriptUrlParsed);
        }
      }}, Fn = Tt(Ce({}, tt), {_private: Ui, execute: function (i, v) {
        var h = yo(Ba, y.turnstileLoadInitTimeTsMs), p = false, o = C(i);
        if (o === null) {
          var g;
          v === undefined && x("Please provide 2 parameters to execute: container and parameters", 43521);
          var L = xe(i, v, "explicit", h);
          p = true, L == null && x("Failed to render widget", 43522), o = (g = kt(L)) !== null && g !== undefined ? g : C(i), o === null && x("Failed to render widget", 43522);
        }
        var _ = y.widgetMap.get(o);
        if (_ !== undefined) {
          var N = p ? false : Ft(_, h);
          k(_, v);
          var F = "".concat(Qt).concat(o);
          if (_.isExecuting) {
            R("Call to execute() on a widget that is already executing (".concat(F, "), consider using reset() before execute().")), N && fr(o, _);
            return;
          }
          if (_.isExecuting = true, _.response !== undefined && _.response !== "") {
            var z;
            _.isExecuting = false, R("Call to execute() on a widget that was already executed (".concat(F, "), execute() will return the previous token obtained. Consider using reset() before execute() to obtain a fresh token.")), N && fr(o, _), (z = _.cbSuccess) === null || z === undefined || z.call(_, _.response, false);
            return;
          }
          _.isExpired && R("Call to execute on a expired-widget (".concat(F, "), consider using reset() before.")), _.isStale && (H(ae.StaleExecute, F), _.isExecuting = true), (_.isResetting || !_.isInitialized) && _.msgQueue.push(Rt.Execute), _.isExecuted = true;
          var q = _.shadow.querySelector("#".concat(F));
          if (q || (_.isExecuting = false, x("Widget ".concat(F, " to execute was not found"), 43522)), _.isResetting || !_.isInitialized) return;
          if (_.msgQueue.length > 0) {
            j(_, o, q), _.params.appearance === ue.Execute && br(q, _);
            return;
          }
          _.params.appearance === ue.Execute && br(q, _), U(_) && me(q, {cs: Ht(_), event: "execute", source: J, widgetId: o}, _.iframeOrigin);
        }
      }, getResponse: function (i) {
        var v = yo(ja, y.turnstileLoadInitTimeTsMs);
        if (typeof i == "undefined") {
          var h = Fe();
          if (h !== undefined) {
            var p = y.widgetMap.get(h);
            return p !== undefined && Ke(h, p, v), (p == null ? undefined : p.isExpired) === true && R("Call to getResponse on a widget that expired, consider refreshing the widget."), p == null ? undefined : p.response;
          }
          x("Could not find a widget", 43794);
        }
        var o = C(i);
        o === null && x("Could not find widget for provided container", 43778);
        var g = y.widgetMap.get(o);
        return g && Ke(o, g, v), g == null ? undefined : g.response;
      }, isExpired: function (i) {
        var v, h = yo(Ka, y.turnstileLoadInitTimeTsMs);
        if (typeof i == "undefined") {
          var p = Fe();
          if (p !== undefined) {
            var o, g = y.widgetMap.get(p);
            return g !== undefined && Ke(p, g, h), (o = g == null ? undefined : g.isExpired) !== null && o !== undefined ? o : false;
          }
          x("Could not find a widget", 43794);
        }
        var L = C(i);
        L === null && x("Could not find widget for provided container", 43778);
        var _ = y.widgetMap.get(L);
        return _ && Ke(L, _, h), (v = _ == null ? undefined : _.isExpired) !== null && v !== undefined ? v : false;
      }, ready: function (i) {
        y.scriptWasLoadedAsync && (R("turnstile.ready() would break if called *before* the Turnstile api.js script is loaded by visitors."), x("Remove async/defer from the Turnstile api.js script tag before using turnstile.ready().", 3857)), typeof i != "function" && x('turnstile.ready() expected a "function" argument, got "'.concat(typeof i == "undefined" ? "undefined" : W(i), '"'), 3841);
        var v = yo(za, y.turnstileLoadInitTimeTsMs);
        Dt(y.gcs, v);
        var h = true, p = false, o = undefined;
        try {
          for (var g = y.widgetMap[Symbol.iterator](), L; !(h = (L = g.next()).done); h = true) {
            var _ = Jn(L.value) || jn(L.value, 2) || Yt(L.value, 2) || Kn(), N = _[0], F = _[1];
            Ke(N, F, v);
          }
        } catch (z) {
          p = true, o = z;
        } finally {
          try {
            !h && g.return != null && g.return();
          } finally {
            if (p) throw o;
          }
        }
        if (y.isReady) {
          i();
          return;
        }
        Dn.push(i);
      }, remove: X, render: Se, reset: ie});
      return Object.defineProperty(Fn, Mi, {configurable: true, enumerable: false, value: {clearPendingApiJsReloadRequest: function () {
        Nn();
      }, rearmTimedUpgrade: function () {
        Pn();
      }, rejectPendingApiJsReloadRequest: function () {
        Pi();
      }, reloadAfterUpgrade: function () {
        B();
      }}}), {runImplicitRender: et, turnstile: Fn};
    }(), xu = function () {
      Hi.runImplicitRender();
    }, Tr = Hi.turnstile;
    function Su(e) {
      var t, r, n = e.getAttribute("data-sitekey"), a = {sitekey: n}, u = e.getAttribute("data-tabindex");
      u !== null && u !== "" && (a.tabindex = Math.trunc(Number(u)));
      var l = e.getAttribute("data-theme");
      l !== null && l !== "" && (["auto", "dark", "light"].indexOf(l) !== -1 ? a.theme = l : R('Unknown data-theme value: "'.concat(l, '".')));
      var d = e.getAttribute("data-size");
      if (d !== null && d !== "" && ([ne.Normal, ne.Compact, ne.Invisible, ne.Flexible].indexOf(d) !== -1 ? a.size = d : R('Unknown data-size value: "'.concat(d, '".'))), 0) var f;
      var s = e.getAttribute("data-action");
      typeof s == "string" && (a.action = s);
      var m = e.getAttribute("data-cdata");
      typeof m == "string" && (a.cData = m);
      var E = e.getAttribute("data-retry");
      E !== null && E !== "" && (["auto", "never"].indexOf(E) !== -1 ? a.retry = E : R('Invalid data-retry value: "'.concat(E, ", expected either 'never' or 'auto'\".")));
      var S = e.getAttribute("data-retry-interval");
      if (S !== null && S !== "") {
        var O = Math.trunc(Number(S));
        O > 0 && O < 9e5 ? a["retry-interval"] = O : R('Invalid data-retry-interval value: "'.concat(S, ', expected an integer value > 0 and < 900000".'));
      }
      var b = e.getAttribute("data-expiry-interval");
      if (b !== null && b !== "") {
        var A = Math.trunc(Number(b));
        A > 0 && A < 36e4 ? a["expiry-interval"] = A : R('Invalid data-expiry-interval value: "'.concat(A, ', expected an integer value > 0 and < 360000".'));
      }
      var P = e.getAttribute("data-refresh-expired");
      P !== null && P !== "" && (["auto", "manual", "never"].indexOf(P) !== -1 ? a["refresh-expired"] = P : R('Unknown data-refresh-expired value: "'.concat(P, ", expected either: 'never', 'auto' or 'manual'.")));
      var I = e.getAttribute("data-refresh-timeout");
      I !== null && I !== "" && (["auto", "manual", "never"].indexOf(I) !== -1 ? a["refresh-timeout"] = I : R('Unknown data-refresh-timeout value: "'.concat(I, ", expected either: 'never', 'auto' or 'manual'.")));
      var M = e.getAttribute("data-language");
      M !== null && M !== "" && (M === "auto" || tu.test(M) ? a.language = M : R('Invalid data-language value: "'.concat(M, ", expected either: auto, or an ISO 639-1 two-letter language code (e.g. en) or language and country code (e.g. en-US).")));
      function C(B) {
        var xe = e.getAttribute(B);
        if (!(xe === null || xe === "")) {
          var Se = Ln(xe);
          return Se === undefined ? undefined : function () {
            for (var et = arguments.length, Fe = new Array(et), tt = 0; tt < et; tt++) Fe[tt] = arguments[tt];
            return Se.apply(undefined, zn(Fe) || Gn(Fe) || Yt(Fe) || Xn());
          };
        }
      }
      var j = ["error-callback", "unsupported-callback", "callback", "expired-callback", "timeout-callback", "after-interactive-callback", "before-interactive-callback"];
      j.forEach(function (B) {
        Object.assign(a, (B in {} ? Object.defineProperty({}, B, {value: C("data-".concat(B)), enumerable: true, configurable: true, writable: true}) : {}[B] = C("data-".concat(B)), {}));
      }), a["feedback-enabled"] = (t = Er(e.getAttribute("data-feedback-enabled"), true, function (B) {
        return 'Invalid data-feedback-enabled value: "'.concat(B, "\", expected either: 'true' or 'false'. Value is ignored.");
      })) !== null && t !== undefined ? t : true, a["response-field"] = (r = Er(e.getAttribute("data-response-field"), true, function (B) {
        return 'Invalid data-response-field value: "'.concat(B, "\", expected either: 'true' or 'false'. Value is ignored.");
      })) !== null && r !== undefined ? r : true;
      var U = e.getAttribute("data-response-field-name");
      U !== null && U !== "" && (a["response-field-name"] = U);
      var k = e.getAttribute("data-execution");
      k !== null && k !== "" && (["render", "execute"].indexOf(k) !== -1 ? a.execution = k : R('Unknown data-execution value: "'.concat(k, ", expected either: 'render' or 'execute'.")));
      var D = e.getAttribute("data-appearance");
      D !== null && D !== "" && (["always", "execute", "interaction-only"].indexOf(D) !== -1 ? a.appearance = D : R('Unknown data-appearance value: "'.concat(D, ", expected either: 'always', 'execute', or 'interaction-only'.")));
      var ie = e.getAttribute("data-offlabel-show-privacy"), H = Er(ie, undefined, function (B) {
        return 'Invalid data-offlabel-show-privacy value: "'.concat(B, '", expected "true" or "false".');
      });
      typeof H == "boolean" && (a["offlabel-show-privacy"] = H);
      var K = e.getAttribute("data-offlabel-show-help"), X = Er(K, undefined, function (B) {
        return 'Invalid data-offlabel-show-help value: "'.concat(B, '", expected "true" or "false".');
      });
      return typeof X == "boolean" && (a["offlabel-show-help"] = X), a;
    }
    function Wi() {
      if (Mn(), Ni()) return false;
      var e = bi(window.turnstile, y);
      return e ? true : (Pn(), false);
    }
    Ze = false, V = Da(), y.scriptWasLoadedAsync = (xr = V == null ? undefined : V.loadedAsync) !== null && xr !== undefined ? xr : false, y.scriptUrl = (Sr = V == null ? undefined : V.src) !== null && Sr !== undefined ? Sr : "undefined", y.scriptUrlParsed = V == null ? undefined : V.url, uu(), (V == null ? undefined : V.params) !== undefined && V.params !== null && (gt = V.params.get("compat"), (gt == null ? undefined : gt.toLowerCase()) === "recaptcha" ? typeof window.grecaptcha == "undefined" ? (R("Compatibility layer enabled."), y.isRecaptchaCompatibilityMode = true, window.grecaptcha = Tr) : R("grecaptcha is already defined. The compatibility layer will not be enabled.") : gt !== null && R('Unknown value for api.js?compat: "'.concat(gt, '", ignoring.')), V.params.forEach(function (e, t) {
      ["onload", "compat", "_cb", "_upgrade", "_reload", "render"].indexOf(t) !== -1 || R('Unknown parameter passed to api.js: "?'.concat(t, '=...", ignoring.'));
    }), Ze = V.params.get("_upgrade") === "true", Pe = V.params.get("onload"), Pe !== null && Pe !== "" && !Ze && setTimeout(function () {
      var e = Ln(Pe);
      e === undefined ? (R("Unable to find onload callback '".concat(Pe, "' immediately after loading, expected 'function', got '").concat(W(Reflect.get(window, Pe)), "'.")), setTimeout(function () {
        var t = Ln(Pe);
        t === undefined ? R("Unable to find onload callback '".concat(Pe, "' after 1 second, expected 'function', got '").concat(W(Reflect.get(window, Pe)), "'.")) : t();
      }, 1e3)) : e();
    }, 0)), Bt = "turnstile" in window, Te = Bt ? Oi(window.turnstile) : undefined, Ir = Bt && Ze ? Ei(window.turnstile, y, function () {
      var e;
      window.turnstile = Tr, (e = Oi(Tr)) === null || e === undefined || e.reloadAfterUpgrade(), sn(y);
    }) : false, Ir && (Te == null || Te.clearPendingApiJsReloadRequest()), Bt && Ze && !Ir ? (R("Turnstile upgrade state was missing. Keeping the existing Turnstile instance."), Te == null || Te.rejectPendingApiJsReloadRequest(), Te == null || Te.rearmTimedUpgrade()) : Bt && !Ze ? R("Turnstile already has been loaded. Was Turnstile imported multiple times?") : (Ir || (window.turnstile = Tr), Ze || ((V == null || (wr = V.params) === null || wr === undefined ? undefined : wr.get("render")) !== "explicit" && Dn.push(xu), document.readyState === "complete" || document.readyState === "interactive" ? setTimeout(ki, 0) : window.addEventListener("DOMContentLoaded", ki)), Pn());
    var xr, Sr, Ze, V, gt, Pe, Bt, Te, Ir, wr;
  }());
}(undefined, undefined));

"""
