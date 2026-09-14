from __future__ import annotations

import typer

import auth.settings as auth_settings
from auth import CanvasAPIError, get_auth_status
from auth.chrome_cookies import resolve_chrome_profile
from auth.inspect import describe_chrome_profiles
from auth.settings import clear_settings, set_selected_profile
from cli.output import choose_profile, emit, fail

settings_app = typer.Typer(help="Saved Chrome profile selection and auth state.")


def _render_selected_profile(saved: dict[str, str]) -> None:
    emit({"selected_profile": saved}, tool_name="settings_choose_profile")


@settings_app.command("show")
def settings_show() -> None:
    try:
        auth = get_auth_status()
    except CanvasAPIError as exc:
        auth = {
            "auth_mode": None,
            "auth_verified": False,
            "auth_status": "error",
            "error": str(exc),
        }
    payload = {
        "settings": auth_settings.load_settings(),
        "auth": auth,
    }
    emit(payload, tool_name="settings_show", failures=False)


@settings_app.command("clear")
def settings_clear() -> None:
    clear_settings()
    emit({"cleared": True}, tool_name="settings_clear")


@settings_app.command("profiles")
def settings_profiles() -> None:
    emit({"profiles": describe_chrome_profiles()}, tool_name="settings_profiles")


@settings_app.command("choose-profile")
def settings_choose_profile(
    profile: str | None = typer.Argument(
        None,
        help="Profile name to save. Omit to choose interactively.",
        show_default=False,
    ),
) -> None:
    if profile:
        resolved = resolve_chrome_profile(profile_name=profile)
        if resolved is None:
            fail("not_found", f"Unknown Chrome profile: {profile}")
        saved = set_selected_profile(name=resolved.name, path=resolved.path)
        _render_selected_profile(saved)
        return

    selected = choose_profile(describe_chrome_profiles())
    saved = set_selected_profile(name=selected["name"], path=selected["path"])
    _render_selected_profile(saved)
