from __future__ import annotations

import asyncio
import base64
import os
from pathlib import Path
from unittest import mock

from fastmcp import Client
from fastmcp.client.transports import StdioTransport
from mcp.types import BlobResourceContents, EmbeddedResource
import pytest

from canvas_mcp.server import mcp
from tools.files import download_course_file, read_course_file


def _download_bytes(payload: bytes):
    def download_file(*, destination_path: str, **_kwargs):
        Path(destination_path).write_bytes(payload)
        return {"content_type": "application/pdf"}

    return download_file


@pytest.mark.parametrize("mime_key", ["content-type", "content_type"])
def test_read_course_file_embeds_downloaded_bytes(mock_client, mime_key):
    payload = b"%PDF-1.4\nexample"
    mock_client.read_file_bytes.return_value = (
        {"display_name": "lecture notes.pdf", mime_key: "application/pdf", "size": len(payload)},
        payload,
    )

    result = read_course_file("12", "34")

    assert len(result.content) == 2
    resource = result.content[1]
    assert isinstance(resource, EmbeddedResource)
    assert isinstance(resource.resource, BlobResourceContents)
    assert resource.resource.mimeType == "application/pdf"
    assert str(resource.resource.uri).endswith("/lecture%20notes.pdf")
    assert base64.b64decode(resource.resource.blob) == payload
    mock_client.read_file_bytes.assert_called_once_with(
        course_id="12", file_id="34", max_bytes=25 * 1024 * 1024
    )


@pytest.mark.parametrize(
    ("metadata", "message"),
    [({"size": 2 * 1024 * 1024}, "2097152 bytes, above"), ({}, "File is above")],
)
def test_read_course_file_reports_oversize(mock_client, metadata, message):
    mock_client.read_file_bytes.return_value = (metadata, None)

    with pytest.raises(ValueError, match=message):
        read_course_file("12", "34", max_size_mb=1)


def _client_with_file(size, response):
    from client import CanvasClient
    from client.base import CanvasClientBase

    file_info = mock.MagicMock(url="https://canvas.example.test/files/34/download?verifier=x")
    file_info.size = size
    canvas = mock.MagicMock()
    canvas.get_course.return_value.get_file.return_value = file_info
    requester = mock.MagicMock(access_token="")
    requester._session.get.return_value.__enter__.return_value = response
    setattr(canvas, "_Canvas__requester", requester)
    patch = mock.patch.object(CanvasClientBase, "_run_with_canvas", lambda self, call: call(canvas))
    return CanvasClient(base_url="https://canvas.example.test"), requester, patch


def test_client_stops_streaming_past_the_limit():
    chunks_read = 0

    def endless(chunk_size):
        nonlocal chunks_read
        while True:
            chunks_read += 1
            yield b"x" * chunk_size

    response = mock.MagicMock(status_code=200, iter_content=endless)
    type(response).content = mock.PropertyMock(side_effect=AssertionError("buffered whole body"))
    client, requester, patch = _client_with_file(None, response)
    with patch:
        _, data = client.read_file_bytes(course_id="12", file_id="34", max_bytes=100_000)
    assert data is None
    assert chunks_read == 2
    assert requester._session.get.call_args.kwargs["stream"] is True


def test_client_skips_download_when_metadata_is_oversize():
    client, requester, patch = _client_with_file(2_000_000, mock.MagicMock())
    with patch:
        _, data = client.read_file_bytes(course_id="12", file_id="34", max_bytes=1_000_000)
    assert data is None
    requester._session.get.assert_not_called()


def test_client_returns_bytes_and_maps_errors():
    from auth import CanvasAPIError

    ok = mock.MagicMock(status_code=200, iter_content=lambda chunk_size: iter([b"ab", b"c"]))
    client, _, patch = _client_with_file(3, ok)
    with patch:
        assert client.read_file_bytes(course_id="12", file_id="34", max_bytes=3)[1] == b"abc"

    client, _, patch = _client_with_file(3, mock.MagicMock(status_code=404))
    with patch, pytest.raises(CanvasAPIError) as exc:
        client.read_file_bytes(course_id="12", file_id="34", max_bytes=3)
    assert exc.value.status_code == 404


def test_existing_download_still_returns_local_path(mock_client, tmp_path):
    payload = b"existing download method"
    mock_client.get_file.return_value = {
        "display_name": "lesson.txt",
        "content_type": "text/plain",
    }
    mock_client.download_file.side_effect = _download_bytes(payload)

    with mock.patch("tools.files.download_dir", return_value=tmp_path):
        result = download_course_file({"course_id": "12", "file_id": "34"})

    assert Path(result["local_path"]).read_bytes() == payload
    assert result["already_present"] is False


def test_mcp_exposes_inline_file_tool(mock_client):
    payload = b"hello from Canvas"
    mock_client.read_file_bytes.return_value = (
        {"display_name": "lesson.txt", "content_type": "text/plain", "size": len(payload)},
        payload,
    )

    async def call_mcp():
        async with Client(mcp) as client:
            names = {tool.name for tool in await client.list_tools()}
            result = await client.call_tool_mcp(
                "read_course_file", {"course_id": "12", "file_id": "34"}
            )
            return names, result

    names, result = asyncio.run(call_mcp())

    assert "read_course_file" in names
    assert "download_course_file" in names
    assert result.isError is not True
    assert any(
        isinstance(item, EmbeddedResource)
        and base64.b64decode(item.resource.blob) == payload
        for item in result.content
    ), repr(result)


def test_mcp_inline_limit_reports_existing_download_option(mock_client):
    mock_client.read_file_bytes.return_value = ({"size": 2 * 1024 * 1024}, None)

    async def call_mcp():
        async with Client(mcp) as client:
            return await client.call_tool_mcp(
                "read_course_file",
                {"course_id": "12", "file_id": "34", "max_size_mb": 1},
            )

    result = asyncio.run(call_mcp())
    assert result.isError is True
    assert "download_course_file" in result.content[0].text


def test_installed_launcher_over_stdio():
    executable = os.getenv("CANVAS_MCP_EXECUTABLE")
    if not executable:
        pytest.skip("Set CANVAS_MCP_EXECUTABLE to test an installed launcher")

    env = {
        **os.environ,
        "CANVAS_BASE_URL": "https://canvas.example.test",
        "CANVAS_SESSION_COOKIE": "local-smoke-test",
        "CANVAS_CSRF_TOKEN": "local-smoke-test",
    }

    async def list_remote_tools():
        transport = StdioTransport(
            executable,
            ["--transport", "stdio"],
            env=env,
            keep_alive=False,
        )
        async with Client(transport) as client:
            return {tool.name for tool in await client.list_tools()}

    names = asyncio.run(list_remote_tools())
    assert "download_course_file" in names
    assert "read_course_file" in names
