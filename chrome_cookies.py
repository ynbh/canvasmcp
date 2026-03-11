from __future__ import annotations

from collections import defaultdict
from http.cookiejar import Cookie
from typing import Iterable
from urllib.parse import urlparse

import browser_cookie3

COOKIE_NAMES = {"canvas_session", "_csrf_token"}


def _domain_from_base_url(base_url: str) -> str:
    parsed = urlparse(base_url)
    return (parsed.hostname or base_url).lstrip(".").lower()


def _normalize_cookie_domain(domain: str) -> str:
    return str(domain).strip().lstrip(".").lower()


def _iter_canvas_cookies(cookies: Iterable[Cookie]) -> dict[str, dict[str, str]]:
    grouped: dict[str, dict[str, str]] = defaultdict(dict)
    for cookie in cookies:
        if cookie.name not in COOKIE_NAMES or not cookie.value:
            continue
        domain = _normalize_cookie_domain(cookie.domain)
        if not domain:
            continue
        grouped[domain][cookie.name] = cookie.value
    return grouped


def detect_canvas_base_url() -> str | None:
    grouped = _iter_canvas_cookies(browser_cookie3.chrome())
    candidates = sorted(
        domain
        for domain, values in grouped.items()
        if COOKIE_NAMES.issubset(values.keys())
    )
    if len(candidates) != 1:
        return None
    return f"https://{candidates[0]}"


def read_chrome_cookies(base_url: str | None = None) -> tuple[str, str] | None:
    domain_name = _domain_from_base_url(base_url) if base_url else None
    cookies = browser_cookie3.chrome(domain_name=domain_name) if domain_name else browser_cookie3.chrome()
    grouped = _iter_canvas_cookies(cookies)

    if domain_name:
        values = grouped.get(domain_name, {})
        if COOKIE_NAMES.issubset(values.keys()):
            return values["canvas_session"], values["_csrf_token"]
        return None

    candidates = [
        values
        for values in grouped.values()
        if COOKIE_NAMES.issubset(values.keys())
    ]
    if len(candidates) != 1:
        return None
    values = candidates[0]
    return values["canvas_session"], values["_csrf_token"]
