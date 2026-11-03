from __future__ import annotations

from unittest import mock

import pytest

import tools.common
from client import CanvasClient


def _no_real_client():
    raise AssertionError(
        "Test built a real Canvas client (it would read browser cookies). "
        "Use the mock_client fixture."
    )


@pytest.fixture(autouse=True)
def _forbid_real_canvas_client(monkeypatch):
    """Fail loudly instead of reading the developer's browser cookies.

    Every tool module shares tools.common.canvas_client, so this one seam
    covers modules added later, unlike patching each module's import.
    """
    tools.common.canvas_client.cache_clear()
    monkeypatch.setattr(tools.common, "create_canvas_client_from_env", _no_real_client)
    yield
    tools.common.canvas_client.cache_clear()


@pytest.fixture
def mock_client(monkeypatch):
    # Autospec so a test stubbing a renamed or misspelled client method fails.
    client = mock.create_autospec(CanvasClient, instance=True)
    monkeypatch.setattr(tools.common, "create_canvas_client_from_env", lambda: client)
    return client
