from __future__ import annotations

from collections import defaultdict
from http.cookiejar import Cookie
from typing import Iterable
from urllib.parse import urlparse

import browser_cookie3

COOKIE_NAMES = {"canvas_session", "_csrf_token"}
IGNORED_CANVAS_DOMAINS = {"canvas-user-content.com"}


def _domain_from_base_url(base_url: str) -> str:
    parsed = urlparse(base_url)
    return (parsed.hostname or base_url).lstrip(".").lower()


def _normalize_cookie_domain(domain: str) -> str:
    return str(domain).strip().lstrip(".").lower()


def _domains_with_complete_canvas_session(
    grouped: dict[str, dict[str, str]],
) -> list[str]:
    return sorted(
        domain
        for domain, values in grouped.items()
        if COOKIE_NAMES.issubset(values) and not _is_ignored_canvas_domain(domain)
    )


def _is_ignored_canvas_domain(domain: str) -> bool:
    normalized = _normalize_cookie_domain(domain)
    return any(
        normalized == ignored or normalized.endswith(f".{ignored}")
        for ignored in IGNORED_CANVAS_DOMAINS
    )


def _prefer_specific_domains(domains: Iterable[str]) -> list[str]:
    normalized = sorted({_normalize_cookie_domain(domain) for domain in domains if domain})
    return [
        domain
        for domain in normalized
        if not any(other != domain and other.endswith(f".{domain}") for other in normalized)
    ]


def _matching_domains(hostname: str, domains: Iterable[str]) -> list[str]:
    normalized_host = _normalize_cookie_domain(hostname)
    matches = [
        domain
        for domain in domains
        if normalized_host == domain or normalized_host.endswith(f".{domain}")
    ]
    return sorted(
        matches,
        key=lambda domain: (normalized_host == domain, len(domain)),
        reverse=True,
    )


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


def list_canvas_cookie_domains() -> list[str]:
    grouped = _iter_canvas_cookies(browser_cookie3.chrome())
    return _prefer_specific_domains(_domains_with_complete_canvas_session(grouped))


def detect_canvas_base_url() -> str | None:
    candidates = list_canvas_cookie_domains()
    if len(candidates) != 1:
        return None
    return f"https://{candidates[0]}"


def read_chrome_cookies(base_url: str | None = None) -> tuple[str, str] | None:
    grouped = _iter_canvas_cookies(browser_cookie3.chrome())
    complete_domains = _domains_with_complete_canvas_session(grouped)

    if base_url:
        domain_name = _domain_from_base_url(base_url)
        matches = _matching_domains(domain_name, complete_domains)
        if matches:
            values = grouped[matches[0]]
            return values["canvas_session"], values["_csrf_token"]
        return None

    candidates = _prefer_specific_domains(complete_domains)
    if len(candidates) != 1:
        return None
    values = grouped[candidates[0]]
    return values["canvas_session"], values["_csrf_token"]
