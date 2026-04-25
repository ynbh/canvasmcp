"""Comprehensive tests for canvasmcp.

Run with: .venv/bin/python -m pytest tests/ -v
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest import mock

import pytest
from typer.testing import CliRunner


# ---------------------------------------------------------------------------
# chrome_cookies tests
# ---------------------------------------------------------------------------


class TestDomainFromBaseUrl:
    """Tests for _domain_from_base_url."""

    def test_extracts_hostname(self):
        from auth.chrome_cookies import _domain_from_base_url

        assert (
            _domain_from_base_url("https://umd.instructure.com")
            == "umd.instructure.com"
        )

    def test_extracts_hostname_with_path(self):
        from auth.chrome_cookies import _domain_from_base_url

        assert (
            _domain_from_base_url("https://canvas.school.edu/api/v1")
            == "canvas.school.edu"
        )

    def test_default_url(self):
        from auth.chrome_cookies import _domain_from_base_url

        assert (
            _domain_from_base_url("https://canvas.instructure.com")
            == "canvas.instructure.com"
        )


class TestReadChromeCookies:
    """Tests for the browser_cookie3 adapter."""

    def test_reads_matching_domain(self):
        from auth.chrome_cookies import read_chrome_cookies

        def cookie(name: str, value: str, domain: str):
            return type("Cookie", (), {"name": name, "value": value, "domain": domain})()

        cookies = [
            cookie("canvas_session", "session123", ".umd.instructure.com"),
            cookie("_csrf_token", "csrf456", ".umd.instructure.com"),
        ]
        with mock.patch("auth.chrome_cookies.browser_cookie3.chrome", return_value=cookies):
            assert read_chrome_cookies("https://umd.instructure.com") == (
                "session123",
                "csrf456",
            )

    def test_reads_parent_domain_for_specific_canvas_host(self):
        from auth.chrome_cookies import read_chrome_cookies

        def cookie(name: str, value: str, domain: str):
            return type("Cookie", (), {"name": name, "value": value, "domain": domain})()

        cookies = [
            cookie("canvas_session", "session123", ".instructure.com"),
            cookie("_csrf_token", "csrf456", ".instructure.com"),
        ]
        with mock.patch("auth.chrome_cookies.browser_cookie3.chrome", return_value=cookies):
            assert read_chrome_cookies("https://umd.instructure.com") == (
                "session123",
                "csrf456",
            )

    def test_detect_canvas_base_url_requires_unique_match(self):
        from auth.chrome_cookies import detect_canvas_base_url

        def cookie(name: str, value: str, domain: str):
            return type("Cookie", (), {"name": name, "value": value, "domain": domain})()

        cookies = [
            cookie("canvas_session", "session123", ".umd.instructure.com"),
            cookie("_csrf_token", "csrf456", ".umd.instructure.com"),
        ]
        with mock.patch("auth.chrome_cookies.browser_cookie3.chrome", return_value=cookies):
            assert detect_canvas_base_url() == "https://umd.instructure.com"

    def test_detect_canvas_base_url_returns_none_for_multiple_domains(self):
        from auth.chrome_cookies import detect_canvas_base_url

        def cookie(name: str, value: str, domain: str):
            return type("Cookie", (), {"name": name, "value": value, "domain": domain})()

        cookies = [
            cookie("canvas_session", "a", ".umd.instructure.com"),
            cookie("_csrf_token", "b", ".umd.instructure.com"),
            cookie("canvas_session", "c", ".school.instructure.com"),
            cookie("_csrf_token", "d", ".school.instructure.com"),
        ]
        with mock.patch("auth.chrome_cookies.browser_cookie3.chrome", return_value=cookies):
            assert detect_canvas_base_url() is None

    def test_detect_canvas_base_url_prefers_specific_domain_over_parent_domain(self):
        from auth.chrome_cookies import detect_canvas_base_url

        def cookie(name: str, value: str, domain: str):
            return type("Cookie", (), {"name": name, "value": value, "domain": domain})()

        cookies = [
            cookie("canvas_session", "parent-session", ".instructure.com"),
            cookie("_csrf_token", "parent-csrf", ".instructure.com"),
            cookie("canvas_session", "child-session", ".umd.instructure.com"),
            cookie("_csrf_token", "child-csrf", ".umd.instructure.com"),
        ]
        with mock.patch("auth.chrome_cookies.browser_cookie3.chrome", return_value=cookies):
            assert detect_canvas_base_url() == "https://umd.instructure.com"

    def test_detect_canvas_base_url_ignores_canvas_user_content_domains(self):
        from auth.chrome_cookies import detect_canvas_base_url

        def cookie(name: str, value: str, domain: str):
            return type("Cookie", (), {"name": name, "value": value, "domain": domain})()

        cookies = [
            cookie("canvas_session", "asset-session", ".cluster47.canvas-user-content.com"),
            cookie("_csrf_token", "asset-csrf", ".cluster47.canvas-user-content.com"),
            cookie("canvas_session", "school-session", ".umd.instructure.com"),
            cookie("_csrf_token", "school-csrf", ".umd.instructure.com"),
        ]
        with mock.patch("auth.chrome_cookies.browser_cookie3.chrome", return_value=cookies):
            assert detect_canvas_base_url() == "https://umd.instructure.com"

    def test_reads_matching_domain_for_specific_profile_path(self):
        from auth.chrome_cookies import read_chrome_cookies

        def cookie(name: str, value: str, domain: str):
            return type("Cookie", (), {"name": name, "value": value, "domain": domain})()

        cookies = [
            cookie("canvas_session", "session123", ".umd.instructure.com"),
            cookie("_csrf_token", "csrf456", ".umd.instructure.com"),
        ]
        with (
            mock.patch("auth.chrome_cookies._cookie_file_for_profile", return_value="/tmp/Cookies"),
            mock.patch("auth.chrome_cookies.browser_cookie3.chrome", return_value=cookies) as chrome,
        ):
            assert read_chrome_cookies(
                "https://umd.instructure.com",
                profile_path="/tmp/Profile 3",
            ) == ("session123", "csrf456")
        assert chrome.call_args.kwargs["cookie_file"].endswith("Cookies")


class TestChromeProfiles:
    def test_list_chrome_profiles_uses_local_state_names(self, tmp_path: Path):
        from auth.chrome_cookies import list_chrome_profiles

        user_data = tmp_path / "Chrome"
        default = user_data / "Default"
        profile_3 = user_data / "Profile 3"
        (default / "Network").mkdir(parents=True)
        (profile_3 / "Network").mkdir(parents=True)
        (default / "Network" / "Cookies").write_text("")
        (profile_3 / "Network" / "Cookies").write_text("")
        (user_data / "Local State").write_text(
            json.dumps(
                {
                    "profile": {
                        "info_cache": {
                            "Default": {"name": "terpmail.umd.edu"},
                            "Profile 3": {"name": "Yashas"},
                        }
                    }
                }
            )
        )

        profiles = list_chrome_profiles(str(user_data))
        assert [profile.name for profile in profiles] == ["terpmail.umd.edu", "Yashas"]


# ---------------------------------------------------------------------------
# auth.urls tests
# ---------------------------------------------------------------------------


class TestNormalizeCanvasApiBaseUrl:
    """Tests for normalize_canvas_api_base_url."""

    def test_adds_api_v1(self):
        from auth.urls import normalize_canvas_api_base_url

        assert normalize_canvas_api_base_url("https://canvas.instructure.com") == (
            "https://canvas.instructure.com/api/v1"
        )

    def test_preserves_existing_api_v1(self):
        from auth.urls import normalize_canvas_api_base_url

        assert normalize_canvas_api_base_url(
            "https://canvas.instructure.com/api/v1"
        ) == ("https://canvas.instructure.com/api/v1")

    def test_extends_api_to_v1(self):
        from auth.urls import normalize_canvas_api_base_url

        assert normalize_canvas_api_base_url("https://canvas.instructure.com/api") == (
            "https://canvas.instructure.com/api/v1"
        )

    def test_strips_trailing_slashes(self):
        from auth.urls import normalize_canvas_api_base_url

        result = normalize_canvas_api_base_url("https://canvas.instructure.com///")
        assert result == "https://canvas.instructure.com/api/v1"

    def test_raises_on_empty(self):
        from auth.urls import normalize_canvas_api_base_url

        with pytest.raises(ValueError, match="empty"):
            normalize_canvas_api_base_url("   ")

    def test_raises_on_no_scheme(self):
        from auth.urls import normalize_canvas_api_base_url

        with pytest.raises(ValueError, match="scheme"):
            normalize_canvas_api_base_url("canvas.instructure.com")


class TestCanvasRootUrl:
    """Tests for canvas_root_url."""

    def test_strips_api_v1(self):
        from auth.urls import canvas_root_url

        assert canvas_root_url("https://canvas.instructure.com/api/v1") == (
            "https://canvas.instructure.com"
        )

    def test_strips_api(self):
        from auth.urls import canvas_root_url

        assert canvas_root_url("https://canvas.instructure.com/api") == (
            "https://canvas.instructure.com"
        )

    def test_no_api_path(self):
        from auth.urls import canvas_root_url

        result = canvas_root_url("https://canvas.instructure.com")
        assert result == "https://canvas.instructure.com"


# ---------------------------------------------------------------------------
# auth tests
# ---------------------------------------------------------------------------


class TestAuthPriority:
    """Tests for Chrome auth configuration."""

    def test_chrome_cookies_first(self):
        cookies = ("session", "csrf")
        with (
            mock.patch("auth.resolve_canvas_base_url", return_value="https://umd.instructure.com"),
            mock.patch("auth._read_chrome_cookies", return_value=cookies),
        ):
            from auth import ensure_canvas_auth_configured

            result = ensure_canvas_auth_configured()
            assert result == "chrome-session"

    def test_raises_when_no_chrome_cookies(self):
        with (
            mock.patch("auth.resolve_canvas_base_url", return_value="https://umd.instructure.com"),
            mock.patch("auth._read_chrome_cookies", return_value=None),
        ):
            from auth import CanvasAPIError, ensure_canvas_auth_configured

            with pytest.raises(CanvasAPIError):
                ensure_canvas_auth_configured()

    def test_uses_env_base_url_override(self):
        with mock.patch.dict(
            os.environ,
            {"CANVAS_BASE_URL": "https://umd.instructure.com"},
            clear=True,
        ):
            from auth.resolve import resolve_canvas_base_url

            assert resolve_canvas_base_url() == "https://umd.instructure.com"

    def test_uses_detected_base_url_when_env_unset(self):
        with (
            mock.patch.dict(os.environ, {}, clear=True),
            mock.patch(
                "auth.chrome_cookies.detect_canvas_base_url",
                return_value="https://umd.instructure.com",
            ),
        ):
            from auth.resolve import resolve_canvas_base_url

            assert resolve_canvas_base_url() == "https://umd.instructure.com"

    def test_inference_error_mentions_chrome_before_env_override(self):
        with (
            mock.patch.dict(os.environ, {}, clear=True),
            mock.patch("auth.resolve.detect_canvas_base_url", return_value=None),
            mock.patch(
                "auth.errors.list_canvas_cookie_domains",
                return_value=["umd.instructure.com", "school.instructure.com"],
            ),
        ):
            from auth.errors import CanvasAPIError
            from auth.resolve import resolve_canvas_base_url

            with pytest.raises(CanvasAPIError) as excinfo:
                resolve_canvas_base_url()

        message = str(excinfo.value)
        assert "Found multiple Canvas sites in Chrome" in message
        assert "Open the target Canvas site in Chrome and retry" in message
        assert "set CANVAS_BASE_URL" in message


class TestCreateCanvasClientFromEnv:
    """Tests for create_canvas_client_from_env."""

    def test_chrome_cookies_sets_cookie_provider(self):
        cookies = ("session_val", "csrf_val")
        with (
            mock.patch("auth.resolve.resolve_canvas_base_url", return_value="https://umd.instructure.com"),
            mock.patch("client._read_chrome_cookies", return_value=cookies),
        ):
            from client import create_canvas_client_from_env

            client = create_canvas_client_from_env()
            assert client.cookie_provider is not None
            assert client.cookie_provider() == cookies
            assert client.base_url == "https://umd.instructure.com"

    def test_raises_without_chrome_cookies(self):
        with (
            mock.patch("auth.resolve.resolve_canvas_base_url", return_value="https://umd.instructure.com"),
            mock.patch("client._read_chrome_cookies", return_value=None),
        ):
            from auth import CanvasAPIError
            from client import create_canvas_client_from_env

            with pytest.raises(CanvasAPIError):
                create_canvas_client_from_env()


class TestGeneratedCli:
    """Smoke tests for the direct Typer CLI."""

    def test_tool_list_outputs_known_tool(self):
        import cli

        runner = CliRunner()
        result = runner.invoke(cli.app, ["tool", "list"])
        assert result.exit_code == 0
        assert "list_courses" in result.stdout

    def test_main_invokes_app(self):
        import cli.bootstrap as cli_boot

        with mock.patch.object(cli_boot, "app") as app:
            cli_boot.main()
            app.assert_called_once_with()

    def test_courses_command_dispatches_expected_args(self):
        import cli
        import cli.bootstrap as cli_boot

        runner = CliRunner()
        with (
            mock.patch.object(cli_boot, "_ensure_auth"),
            mock.patch.object(cli_boot, "dispatch_tool_call") as dispatch,
        ):
            dispatch.return_value = {"count": 0, "courses": []}
            result = runner.invoke(cli.app, ["courses", "--all", "--limit", "10"])
        assert result.exit_code == 0
        dispatch.assert_called_once_with(
            "list_courses",
            {"favorites_only": False, "search": None, "limit": 10},
        )

    def test_today_does_not_require_auth(self):
        import cli
        import cli.bootstrap as cli_boot

        runner = CliRunner()
        with (
            mock.patch.object(cli_boot, "_ensure_auth") as ensure_auth,
            mock.patch.object(cli_boot, "dispatch_tool_call") as dispatch,
        ):
            dispatch.return_value = {"today": "2026-03-10"}
            result = runner.invoke(cli.app, ["today"])
        assert result.exit_code == 0
        ensure_auth.assert_not_called()

    def test_auth_status_reports_env_override(self):
        import cli
        import cli.bootstrap as cli_boot

        runner = CliRunner()
        with mock.patch.object(
            cli_boot,
            "get_auth_status",
            return_value={
                "auth_mode": "chrome-session",
                "resolved_canvas_base_url": "https://umd.instructure.com",
                "auth_status": "verified",
            },
        ):
            result = runner.invoke(cli.app, ["auth-status"])
        assert result.exit_code == 0
        assert "chrome-session" in result.stdout
        assert "umd.instructure.com" in result.stdout

    def test_auth_status_returns_json_error_instead_of_exiting(self):
        import cli
        import cli.bootstrap as cli_boot

        runner = CliRunner()
        with mock.patch.object(
            cli_boot,
            "get_auth_status",
            return_value={
                "auth_mode": None,
                "auth_status": "not_logged_in",
                "error": "No usable Canvas session",
            },
        ):
            result = runner.invoke(cli.app, ["auth-status"])
        assert result.exit_code == 0
        assert '"auth_mode": null' in result.stdout
        assert "No usable Canvas session" in result.stdout

    def test_auth_status_catches_canvas_api_error_and_returns_json(self):
        import cli
        import cli.bootstrap as cli_boot
        from auth import CanvasAPIError

        runner = CliRunner()
        with mock.patch.object(
            cli_boot,
            "get_auth_status",
            side_effect=CanvasAPIError("Could not infer a Canvas site from Chrome"),
        ):
            result = runner.invoke(cli.app, ["auth-status"])
        assert result.exit_code == 0
        assert '"auth_status": "error"' in result.stdout
        assert "Could not infer a Canvas site from Chrome" in result.stdout
        assert "Traceback" not in result.stdout

    def test_settings_show_reports_saved_profile_and_auth(self):
        import cli
        import cli.settings as settings_mod

        runner = CliRunner()
        with (
            mock.patch(
                "auth.settings.load_settings",
                return_value={"chrome_profile_name": "terpmail.umd.edu"},
            ),
            mock.patch.object(
                settings_mod,
                "get_auth_status",
                return_value={"auth_status": "verified"},
            ),
        ):
            result = runner.invoke(cli.app, ["settings", "show"])
        assert result.exit_code == 0
        assert "terpmail.umd.edu" in result.stdout
        assert "verified" in result.stdout

    def test_settings_show_catches_canvas_api_error_and_returns_json(self):
        import cli
        import cli.settings as settings_mod
        from auth import CanvasAPIError

        runner = CliRunner()
        with (
            mock.patch(
                "auth.settings.load_settings",
                return_value={"chrome_profile_name": "terpmail.umd.edu"},
            ),
            mock.patch.object(
                settings_mod,
                "get_auth_status",
                side_effect=CanvasAPIError("Could not infer a Canvas site from Chrome"),
            ),
        ):
            result = runner.invoke(cli.app, ["settings", "show"])
        assert result.exit_code == 0
        assert '"auth_status": "error"' in result.stdout
        assert "Could not infer a Canvas site from Chrome" in result.stdout
        assert "Traceback" not in result.stdout

    def test_settings_profiles_outputs_profile_statuses(self):
        import cli

        runner = CliRunner()
        with mock.patch(
            "cli.settings.describe_chrome_profiles",
            return_value=[
                {"name": "terpmail.umd.edu", "auth_status": "verified"},
                {"name": "Yashas", "auth_status": "not_logged_in"},
            ],
        ):
            result = runner.invoke(cli.app, ["settings", "profiles"])
        assert result.exit_code == 0
        assert "verified" in result.stdout
        assert "not_logged_in" in result.stdout

    def test_settings_choose_profile_headless_accepts_explicit_name(self):
        import cli

        runner = CliRunner()
        resolved = type(
            "ResolvedProfile",
            (),
            {"name": "terpmail.umd.edu", "path": "/tmp/Default"},
        )()
        with (
            mock.patch(
                "cli.settings.resolve_chrome_profile",
                return_value=resolved,
            ),
            mock.patch(
                "cli.settings.set_selected_profile",
                return_value={
                    "chrome_profile_name": "terpmail.umd.edu",
                    "chrome_profile_path": "/tmp/Default",
                },
            ) as save,
        ):
            result = runner.invoke(
                cli.app,
                ["settings", "choose-profile", "terpmail.umd.edu"],
            )
        assert result.exit_code == 0
        save.assert_called_once_with(name="terpmail.umd.edu", path="/tmp/Default")

    def test_courses_command_renders_clean_auth_error(self):
        import cli
        import cli.bootstrap as cli_boot
        from auth import CanvasAPIError

        runner = CliRunner()
        with mock.patch.object(
            cli_boot,
            "ensure_canvas_auth_configured",
            side_effect=CanvasAPIError("Open Canvas in Chrome and retry"),
        ):
            result = runner.invoke(cli.app, ["courses"])
        assert result.exit_code == 1
        assert "Error: Open Canvas in Chrome and retry" in result.stdout
        assert "Traceback" not in result.stdout


class TestMcpServerEntrypoint:
    """Tests for the FastMCP server entrypoint."""

    def test_main_defaults_to_stdio(self):
        import canvas_mcp
        import canvas_mcp.server as mcp_srv

        with (
            mock.patch.object(mcp_srv, "ensure_canvas_auth_configured"),
            mock.patch.object(canvas_mcp.mcp, "run") as run,
        ):
            canvas_mcp.main([])

        run.assert_called_once_with("stdio", show_banner=True)

    def test_main_supports_http_transport(self):
        import canvas_mcp
        import canvas_mcp.server as mcp_srv

        with (
            mock.patch.object(mcp_srv, "ensure_canvas_auth_configured"),
            mock.patch.object(canvas_mcp.mcp, "run") as run,
        ):
            canvas_mcp.main(
                [
                    "--transport",
                    "http",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    "8000",
                    "--path",
                    "/mcp",
                    "--no-banner",
                ]
            )

        run.assert_called_once_with(
            "http",
            show_banner=False,
            host="127.0.0.1",
            port=8000,
            path="/mcp",
        )
