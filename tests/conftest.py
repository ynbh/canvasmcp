from __future__ import annotations

from unittest import mock

import browser_cookie3
import pytest
import requests

import tools.common
from client import CanvasClient


def _forbid(what: str):
    # pytest.fail raises a BaseException, so tool code that catches Exception
    # (dispatch_tool_call, schedule.fire, ...) can't swallow it.
    def _fail(*_args, **_kwargs):
        pytest.fail(f"Test tried to {what}. Use the mock_client fixture or a stub.", pytrace=True)

    return _fail


def _fixture_cookie_file_only(reader):
    def _read(*args, **kwargs):
        if not kwargs.get("cookie_file"):
            pytest.fail(
                "Test tried to read the real browser cookie store. "
                "Stub it, or pass cookie_file= pointing at a fixture.",
                pytrace=True,
            )
        return reader(*args, **kwargs)

    return _read


@pytest.fixture(autouse=True)
def _isolate_from_real_environment(monkeypatch, tmp_path):
    """Keep tests away from real cookies, the network, and the real home directory."""
    monkeypatch.setattr(browser_cookie3, "chrome", _fixture_cookie_file_only(browser_cookie3.chrome))
    monkeypatch.setattr(browser_cookie3, "firefox", _fixture_cookie_file_only(browser_cookie3.firefox))
    monkeypatch.setattr(requests.Session, "send", _forbid("make a real HTTP request"))
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    # Every tool module shares tools.common.canvas_client, so one patch covers them all.
    tools.common.canvas_client.cache_clear()
    monkeypatch.setattr(
        tools.common, "create_canvas_client_from_env", _forbid("build a real Canvas client")
    )
    yield
    tools.common.canvas_client.cache_clear()


def autospec_client() -> mock.MagicMock:
    # Autospec so stubbing a renamed or misspelled client method fails.
    return mock.create_autospec(CanvasClient, instance=True)


@pytest.fixture
def mock_client(monkeypatch):
    client = autospec_client()
    monkeypatch.setattr(tools.common, "create_canvas_client_from_env", lambda: client)
    return client
