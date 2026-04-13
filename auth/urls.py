from __future__ import annotations

from urllib.parse import urlparse, urlunparse


def normalize_canvas_api_base_url(base_url: str) -> str:
    raw = base_url.strip().rstrip("/")
    if not raw:
        raise ValueError("Canvas base URL cannot be empty")

    parsed = urlparse(raw)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(
            "Canvas base URL must include scheme and host, e.g. https://school.instructure.com"
        )

    path = parsed.path.rstrip("/")
    if path.endswith("/api/v1"):
        api_path = path
    elif path.endswith("/api"):
        api_path = f"{path}/v1"
    elif not path:
        api_path = "/api/v1"
    else:
        api_path = f"{path}/api/v1"

    return urlunparse(parsed._replace(path=api_path, params="", query="", fragment=""))


def canvas_root_url(base_url: str) -> str:
    api_url = normalize_canvas_api_base_url(base_url)
    parsed = urlparse(api_url)
    path = parsed.path.rstrip("/")

    if path.endswith("/api/v1"):
        root_path = path[: -len("/api/v1")]
    elif path.endswith("/api"):
        root_path = path[: -len("/api")]
    else:
        root_path = path

    root = urlunparse(
        parsed._replace(path=root_path or "", params="", query="", fragment="")
    )
    return root.rstrip("/")
