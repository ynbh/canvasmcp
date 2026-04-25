from __future__ import annotations

from unittest import mock

import pytest


@pytest.fixture
def mock_client():
    client = mock.MagicMock()
    patches = [
        mock.patch("tools.assignments.canvas_client", return_value=client),
        mock.patch("tools.common.canvas_client", return_value=client),
        mock.patch("tools.courses.canvas_client", return_value=client),
        mock.patch("tools.discussions.canvas_client", return_value=client),
        mock.patch("tools.files.canvas_client", return_value=client),
        mock.patch("tools.grades.canvas_client", return_value=client),
        mock.patch("tools.misc.canvas_client", return_value=client),
        mock.patch("tools.submissions.canvas_client", return_value=client),
    ]
    for patch in patches:
        patch.start()
    try:
        yield client
    finally:
        for patch in reversed(patches):
            patch.stop()
