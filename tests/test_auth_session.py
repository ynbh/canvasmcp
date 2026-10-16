import os
from unittest import mock

import pytest
import requests
from browser_cookie3 import create_cookie

from auth import CanvasAPIError
from auth.probe import get_auth_status
from auth.session import apply_chrome_session_to_http_session, read_chrome_session_cookies


def _firefox_cookie(domain, name, value, expires=None):
    return create_cookie(domain, "/", True, expires, name, value, True)


def test_firefox_auth_verifies_without_reading_chrome():
    jar = [_firefox_cookie("canvas.example.test", name, value) for name, value in
           [("canvas_session", "session-value"), ("_csrf_token", "csrf-value")]]
    response = mock.Mock(status_code=200, headers={"content-type": "application/json"})
    with (
        mock.patch.dict(os.environ, {"CANVAS_COOKIE_BROWSER": "firefox",
            "CANVAS_BASE_URL": "https://canvas.example.test", "CANVAS_SESSION_COOKIE": "",
            "CANVAS_CSRF_TOKEN": ""}),
        mock.patch("auth.session.browser_cookie3.firefox", return_value=jar) as firefox,
        mock.patch("auth.session.read_chrome_cookies") as chrome,
        mock.patch("auth.probe.list_canvas_cookie_domains_for_profile") as discovery,
        mock.patch("auth.probe.requests.Session.get", return_value=response),
    ):
        status = get_auth_status()
    assert status["auth_verified"] is True
    assert status["auth_mode"] == "firefox-session"
    firefox.assert_called_once_with(domain_name="example.test")
    chrome.assert_not_called()
    discovery.assert_not_called()


@pytest.mark.parametrize("domain,expires", [("canvas.example.test.attacker.test", None),
                                              ("canvas.example.test", 1)])
def test_firefox_rejects_wrong_domain_and_expired_cookies(domain, expires):
    jar = [_firefox_cookie(domain, name, "secret", expires) for name in
           ["canvas_session", "_csrf_token"]]
    with (
        mock.patch.dict(os.environ, {"CANVAS_COOKIE_BROWSER": "firefox",
            "CANVAS_SESSION_COOKIE": "", "CANVAS_CSRF_TOKEN": ""}),
        mock.patch("auth.session.browser_cookie3.firefox", return_value=jar),
    ):
        with pytest.raises(CanvasAPIError, match="Log into"):
            read_chrome_session_cookies("https://canvas.example.test")


def test_firefox_reads_parent_domain_cookies_from_sqlite(tmp_path):
    import sqlite3

    import browser_cookie3

    cookie_file = tmp_path / "cookies.sqlite"
    with sqlite3.connect(cookie_file) as con:
        con.execute(
            "create table moz_cookies (host text, path text, isSecure int, expiry int,"
            " name text, value text, isHttpOnly int)"
        )
        con.executemany(
            "insert into moz_cookies values (?, '/', 1, 4102444800, ?, ?, 1)",
            [
                (".example.test", "canvas_session", "parent-session"),
                (".example.test", "_csrf_token", "parent-csrf"),
                (".other.example.test", "canvas_session", "sibling-session"),
                (".other.example.test", "_csrf_token", "sibling-csrf"),
            ],
        )
    real_firefox = browser_cookie3.firefox
    with (
        mock.patch.dict(os.environ, {"CANVAS_COOKIE_BROWSER": "firefox",
            "CANVAS_SESSION_COOKIE": "", "CANVAS_CSRF_TOKEN": ""}),
        mock.patch(
            "auth.session.browser_cookie3.firefox",
            lambda **kw: real_firefox(cookie_file=str(cookie_file), **kw),
        ),
    ):
        cookies = read_chrome_session_cookies("https://canvas.school.example.test")
    assert cookies == ("parent-session", "parent-csrf")


def test_cookie_env_bypasses_chrome_decryption():
    with (
        mock.patch.dict(
            os.environ,
            {"CANVAS_SESSION_COOKIE": "session-value", "CANVAS_CSRF_TOKEN": "csrf-value"},
        ),
        mock.patch("auth.session.read_chrome_cookies") as browser_read,
    ):
        cookies = read_chrome_session_cookies("https://canvas.example.test")

    assert cookies == ("session-value", "csrf-value")
    browser_read.assert_not_called()


def test_cookie_env_requires_both_values():
    with mock.patch.dict(
        os.environ,
        {"CANVAS_SESSION_COOKIE": "session-value", "CANVAS_CSRF_TOKEN": ""},
    ):
        with pytest.raises(CanvasAPIError, match="Set both CANVAS_SESSION_COOKIE"):
            read_chrome_session_cookies("https://canvas.example.test")


def test_cookie_env_auth_probe_uses_canvas_session_without_chrome():
    response = mock.Mock(status_code=200, headers={"content-type": "application/json"})
    with (
        mock.patch.dict(
            os.environ,
            {
                "CANVAS_BASE_URL": "https://canvas.example.test",
                "CANVAS_SESSION_COOKIE": "session-value",
                "CANVAS_CSRF_TOKEN": "csrf-value",
            },
        ),
        mock.patch("auth.session.read_chrome_cookies") as browser_read,
        mock.patch("auth.probe.requests.Session.get", return_value=response) as get,
    ):
        status = get_auth_status()

    assert status["auth_mode"] == "cookie-env"
    assert status["auth_verified"] is True
    assert status["auth_status"] == "verified"
    browser_read.assert_not_called()
    assert get.call_args.args[0] == "https://canvas.example.test/api/v1/users/self"


@pytest.mark.parametrize(
    ("cookie_token", "header_token"),
    [
        ("token%2Bvalue%2Fpart%3D%3D", "token+value/part=="),
        ("token+value/part==", "token+value/part=="),
    ],
)
def test_csrf_header_is_decoded_and_cookie_is_preserved(cookie_token, header_token):
    with requests.Session() as session:
        apply_chrome_session_to_http_session(
            session,
            base_url="https://school.instructure.com",
            cookies=("session-value", cookie_token),
        )
        request = session.prepare_request(
            requests.Request("POST", "https://school.instructure.com/api/v1/files")
        )

    assert request.headers["X-CSRF-Token"] == header_token
    assert f"_csrf_token={cookie_token}" in request.headers["Cookie"]
    assert "canvas_session=session-value" in request.headers["Cookie"]
