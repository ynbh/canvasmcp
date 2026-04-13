from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from http.cookiejar import Cookie
import json
import os
from pathlib import Path
import sys
from typing import Iterable
from urllib.parse import urlparse

import browser_cookie3

COOKIE_NAMES = {"canvas_session", "_csrf_token"}
IGNORED_CANVAS_DOMAINS = {"canvas-user-content.com"}


@dataclass(slots=True)
class ChromeProfile:
    name: str
    path: str
    cookie_file: str | None


def _default_chrome_user_data_dir() -> Path | None:
    home = Path.home()
    if sys.platform == "darwin":
        return home / "Library/Application Support/Google/Chrome"
    if sys.platform.startswith("linux"):
        return home / ".config/google-chrome"
    if sys.platform.startswith("win"):
        local_app_data = os.getenv("LOCALAPPDATA", "").strip()
        if local_app_data:
            return Path(local_app_data) / "Google/Chrome/User Data"
    return None


def _cookie_file_for_profile(profile_path: str | Path) -> str | None:
    profile_dir = Path(profile_path)
    for candidate in ("Network/Cookies", "Cookies"):
        cookie_file = profile_dir / candidate
        if cookie_file.exists():
            return str(cookie_file)
    return None


def _profile_name_map(user_data_dir: Path) -> dict[str, str]:
    local_state = user_data_dir / "Local State"
    try:
        payload = json.loads(local_state.read_text())
    except (FileNotFoundError, OSError, ValueError, TypeError):
        return {}
    info_cache = payload.get("profile", {}).get("info_cache", {})
    if not isinstance(info_cache, dict):
        return {}
    mapping: dict[str, str] = {}
    for directory, info in info_cache.items():
        if not isinstance(info, dict):
            continue
        name = str(info.get("name", "")).strip()
        if name:
            mapping[directory] = name
    return mapping


def list_chrome_profiles(user_data_dir: str | None = None) -> list[ChromeProfile]:
    root = Path(user_data_dir) if user_data_dir else _default_chrome_user_data_dir()
    if root is None or not root.exists():
        return []
    name_map = _profile_name_map(root)
    profiles: list[ChromeProfile] = []
    for child in sorted(root.iterdir(), key=lambda entry: entry.name):
        if not child.is_dir():
            continue
        if child.name == "System Profile":
            continue
        if child.name != "Default" and not child.name.startswith("Profile "):
            continue
        label = name_map.get(child.name, child.name)
        profiles.append(
            ChromeProfile(
                name=label,
                path=str(child),
                cookie_file=_cookie_file_for_profile(child),
            )
        )
    return profiles


def resolve_chrome_profile(
    *,
    profile_name: str | None = None,
    profile_path: str | None = None,
    user_data_dir: str | None = None,
) -> ChromeProfile | None:
    if profile_path:
        path = str(Path(profile_path).expanduser())
        return ChromeProfile(
            name=Path(path).name,
            path=path,
            cookie_file=_cookie_file_for_profile(path),
        )
    if not profile_name:
        return None

    query = profile_name.strip().casefold()
    if not query:
        return None

    matches = [
        profile
        for profile in list_chrome_profiles(user_data_dir=user_data_dir)
        if profile.name.casefold() == query
        or Path(profile.path).name.casefold() == query
    ]
    if len(matches) == 1:
        return matches[0]
    return None


def _chrome_cookies(
    *,
    domain_name: str = "",
    profile_path: str | None = None,
) -> Iterable[Cookie]:
    kwargs: dict[str, str] = {"domain_name": domain_name}
    if profile_path:
        cookie_file = _cookie_file_for_profile(profile_path)
        if not cookie_file:
            return []
        kwargs["cookie_file"] = cookie_file
    return browser_cookie3.chrome(**kwargs)


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


def list_canvas_cookie_domains(profile_path: str | None = None) -> list[str]:
    grouped = _iter_canvas_cookies(_chrome_cookies(profile_path=profile_path))
    return _prefer_specific_domains(_domains_with_complete_canvas_session(grouped))


def detect_canvas_base_url(profile_path: str | None = None) -> str | None:
    candidates = list_canvas_cookie_domains(profile_path=profile_path)
    if len(candidates) != 1:
        return None
    return f"https://{candidates[0]}"


def read_chrome_cookies(
    base_url: str | None = None,
    *,
    profile_path: str | None = None,
) -> tuple[str, str] | None:
    grouped = _iter_canvas_cookies(_chrome_cookies(profile_path=profile_path))
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
