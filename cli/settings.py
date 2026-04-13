from __future__ import annotations

import json
import sys

import typer
from rich.console import Console

from auth import CanvasAPIError, get_auth_status
from auth.inspect import describe_chrome_profiles
from auth.chrome_cookies import resolve_chrome_profile
from auth.settings import clear_settings, load_settings, set_selected_profile

console = Console()
settings_app = typer.Typer(help="Saved Chrome profile selection and auth state.")


def _render_selected_profile(saved: dict[str, str]) -> None:
    console.print_json(json.dumps({"selected_profile": saved}, default=str))


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
        "settings": load_settings(),
        "auth": auth,
    }
    console.print_json(json.dumps(payload, default=str))


@settings_app.command("clear")
def settings_clear() -> None:
    clear_settings()
    console.print_json(json.dumps({"cleared": True}))


@settings_app.command("profiles")
def settings_profiles() -> None:
    console.print_json(json.dumps({"profiles": describe_chrome_profiles()}, default=str))


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
            console.print(f"[bold red]Error:[/bold red] Unknown Chrome profile: {profile}")
            raise typer.Exit(1)
        saved = set_selected_profile(name=resolved.name, path=resolved.path)
        _render_selected_profile(saved)
        return

    profiles = describe_chrome_profiles()
    if not sys.stdin.isatty():
        console.print(
            "[bold red]Error:[/bold red] choose-profile requires a TTY. "
            'Use `canvas settings choose-profile "<name>"` in headless mode.'
        )
        raise typer.Exit(1)
    if not profiles:
        console.print("[bold red]Error:[/bold red] No profiles found")
        raise typer.Exit(1)

    for index, item in enumerate(profiles, start=1):
        domain = (
            item["resolved_canvas_base_url"]
            or ", ".join(item["detected_canvas_domains"])
            or "-"
        )
        marker = "*" if item["selected"] else " "
        console.print(f"{index}. {marker} {item['name']} [{item['auth_status']}] {domain}")

    choice = typer.prompt("Select profile number")
    try:
        selected = profiles[int(choice) - 1]
    except (ValueError, IndexError):
        console.print("[bold red]Error:[/bold red] Invalid profile selection")
        raise typer.Exit(1)

    saved = set_selected_profile(name=selected["name"], path=selected["path"])
    _render_selected_profile(saved)
