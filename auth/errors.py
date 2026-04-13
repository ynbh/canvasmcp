from __future__ import annotations

from .chrome_cookies import list_canvas_cookie_domains

from .profiles import resolve_chrome_profile_path


class CanvasAPIError(RuntimeError):
    pass


def format_domain_list(domains: list[str]) -> str:
    shown = domains[:5]
    suffix = "" if len(domains) <= 5 else f", +{len(domains) - 5} more"
    return ", ".join(shown) + suffix


def base_url_inference_error(
    *,
    profile_name: str | None = None,
    profile_path: str | None = None,
) -> CanvasAPIError:
    try:
        domains = list_canvas_cookie_domains(
            profile_path=resolve_chrome_profile_path(
                profile_name=profile_name,
                profile_path=profile_path,
            )
        )
    except Exception as exc:
        return CanvasAPIError(
            "Could not inspect Chrome for Canvas sessions. "
            f"{str(exc).strip() or 'Chrome cookies could not be read.'}"
        )
    if not domains:
        return CanvasAPIError(
            "Could not infer a Canvas site from Chrome. "
            "Open your school's Canvas in Chrome, make sure you're signed in, and retry."
        )
    if len(domains) > 1:
        return CanvasAPIError(
            "Found multiple Canvas sites in Chrome: "
            f"{format_domain_list(domains)}. "
            "Auto-detection needs exactly one. Open the target Canvas site in Chrome and retry. "
            "If you need to pin one explicitly, set CANVAS_BASE_URL."
        )
    return CanvasAPIError(
        "Could not infer a Canvas site from Chrome. "
        "Open your school's Canvas in Chrome and retry."
    )


def missing_chrome_session_error(
    base_url: str,
    *,
    profile_name: str | None = None,
    profile_path: str | None = None,
) -> CanvasAPIError:
    try:
        domains = list_canvas_cookie_domains(
            profile_path=resolve_chrome_profile_path(
                profile_name=profile_name,
                profile_path=profile_path,
            )
        )
    except Exception as exc:
        return CanvasAPIError(
            "Could not read Chrome cookies for the resolved Canvas site "
            f"({base_url}). {str(exc).strip() or 'Chrome cookies could not be read.'}"
        )
    if not domains:
        return CanvasAPIError(
            f"No usable Canvas session was found in Chrome for {base_url}. "
            "Open that site in Chrome, sign in, and retry."
        )
    return CanvasAPIError(
        f"No usable Canvas session was found in Chrome for {base_url}. "
        f"Chrome currently has Canvas sessions for: {format_domain_list(domains)}. "
        "Sign into the target site in Chrome and retry."
    )
