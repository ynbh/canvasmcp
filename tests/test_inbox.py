from __future__ import annotations

from unittest import mock

import pytest


def _client_with_requester():
    """A real CanvasClient whose Canvas requester is a mock, so tests see the exact requests."""
    from client import CanvasClient
    from client.base import CanvasClientBase

    requester = mock.MagicMock()
    canvas = mock.MagicMock()
    setattr(canvas, "_Canvas__requester", requester)
    patch = mock.patch.object(
        CanvasClientBase, "_run_with_canvas", lambda self, call: call(canvas)
    )
    return CanvasClient(base_url="https://canvas.example.test"), requester, patch


class TestInboxClient:
    def test_get_conversation_never_marks_it_read(self):
        client, requester, patch = _client_with_requester()
        requester.request.return_value.json.return_value = {"id": 42, "messages": []}
        with patch:
            client.get_conversation(conversation_id="42")
        method, endpoint = requester.request.call_args.args[:2]
        assert (method, endpoint) == ("GET", "conversations/42")
        assert ("auto_mark_as_read", "false") in requester.request.call_args.kwargs["_kwargs"]

    @pytest.mark.parametrize(
        ("scope", "course_id", "expected", "absent"),
        [
            (None, None, [], ["scope", "filter[]"]),
            ("unread", None, [("scope", "unread")], ["filter[]"]),
            ("sent", "123", [("scope", "sent"), ("filter[]", "course_123")], []),
        ],
    )
    def test_list_conversations_params(self, scope, course_id, expected, absent):
        client, _, patch = _client_with_requester()
        with patch, mock.patch("client.base.PaginatedList", return_value=[]) as paginated:
            client.list_conversations(scope=scope, course_id=course_id)
        args = paginated.call_args
        assert args.args[2:4] == ("GET", "conversations")
        sent = args.kwargs["_kwargs"]
        for pair in expected:
            assert pair in sent
        for key in absent:
            assert key not in [k for k, _ in sent]

    def test_inbox_client_only_reads(self):
        client, requester, patch = _client_with_requester()
        requester.request.return_value.json.return_value = {"id": 1, "messages": []}
        with patch, mock.patch("client.base.PaginatedList", return_value=[]) as paginated:
            client.list_conversations(scope="unread")
            client.get_conversation(conversation_id="1")
        assert all(call.args[0] == "GET" for call in requester.request.call_args_list)
        assert all(call.args[2] == "GET" for call in paginated.call_args_list)


class TestListInboxConversationsTool:
    def test_defaults_to_inbox_without_sending_a_scope(self, mock_client):
        from tools import list_inbox_conversations

        mock_client.list_conversations.return_value = []
        result = list_inbox_conversations({})
        assert result["scope"] == "inbox"
        assert mock_client.list_conversations.call_args.kwargs["scope"] is None

    def test_rejects_unknown_scope_and_bad_course_id(self, mock_client):
        from tools import list_inbox_conversations

        assert list_inbox_conversations({"scope": "trash"})["error"] == "invalid_argument"
        assert list_inbox_conversations({"course_id": "../1"})["error"] == "invalid_argument"
        mock_client.list_conversations.assert_not_called()

    def test_maps_summaries(self, mock_client):
        from tools import list_inbox_conversations

        mock_client.list_conversations.return_value = [
            {
                "id": 7,
                "subject": "Exam 2",
                "workflow_state": "unread",
                "last_message": "x" * 1000,
                "last_message_at": "2026-10-05T14:00:00Z",
                "message_count": 2,
                "context_name": "MATH101",
                "participants": [{"id": 1, "name": "Prof"}, {"id": 2, "full_name": "Student A"}],
                "properties": ["attachments"],
            }
        ]
        result = list_inbox_conversations({"scope": "unread", "course_id": "123"})
        conversation = result["conversations"][0]
        assert conversation["id"] == "7" and conversation["workflow_state"] == "unread"
        assert len(conversation["last_message_preview"]) == 300
        assert conversation["participants"] == ["Prof", "Student A"]
        assert conversation["has_attachments"] is True
        assert mock_client.list_conversations.call_args.kwargs["course_id"] == "123"


def test_sent_conversations_fall_back_to_your_last_message(mock_client):
    from tools import list_inbox_conversations

    mock_client.list_conversations.return_value = [
        {
            "id": 8,
            "last_message": None,
            "last_message_at": None,
            "last_authored_message": "Can I come to office hours?",
            "last_authored_message_at": "2026-10-04T09:00:00Z",
        }
    ]
    conversation = list_inbox_conversations({"scope": "sent"})["conversations"][0]
    assert conversation["last_message_preview"] == "Can I come to office hours?"
    assert conversation["last_message_at"] == "2026-10-04T09:00:00Z"


class TestGetInboxConversationTool:
    def test_requires_a_numeric_id(self, mock_client):
        from tools import get_inbox_conversation

        assert get_inbox_conversation({})["error"] == "missing_argument"
        assert get_inbox_conversation({"conversation_id": "1/../2"})["error"] == "invalid_argument"
        mock_client.get_conversation.assert_not_called()

    def test_maps_messages_and_hides_attachment_urls(self, mock_client):
        from tools import get_inbox_conversation

        mock_client.get_conversation.return_value = {
            "id": 7,
            "subject": "Exam 2",
            "workflow_state": "unread",
            "participants": [{"id": 1, "name": "Prof"}, {"id": 2, "name": "Me"}],
            "messages": [
                {
                    "id": 11,
                    "author_id": 1,
                    "created_at": "2026-10-05T14:00:00Z",
                    "body": "Exam moved to Friday.",
                    "attachments": [
                        {
                            "id": 99,
                            "display_name": "review.pdf",
                            "content-type": "application/pdf",
                            "size": 1234,
                            "url": "https://canvas.example.test/files/99/download?verifier=SECRET",
                        }
                    ],
                }
            ],
        }
        result = get_inbox_conversation({"conversation_id": "7"})
        message = result["messages"][0]
        assert result["workflow_state"] == "unread"
        assert message["author"] == "Prof" and message["body"] == "Exam moved to Friday."
        assert message["attachments"] == [
            {"id": "99", "display_name": "review.pdf", "content_type": "application/pdf", "size": 1234}
        ]
        assert "SECRET" not in repr(result)


def test_long_message_bodies_say_they_were_truncated(mock_client):
    from tools import get_inbox_conversation
    from tools.common import DEFAULT_HTML_CHAR_LIMIT

    mock_client.get_conversation.return_value = {
        "id": 7,
        "participants": [],
        "messages": [
            {"id": 1, "author_id": 1, "body": "a" * (DEFAULT_HTML_CHAR_LIMIT + 1)},
            {"id": 2, "author_id": 1, "body": "short"},
        ],
    }
    long, short = get_inbox_conversation({"conversation_id": "7"})["messages"]
    assert long["body_truncated"] is True and len(long["body"]) == DEFAULT_HTML_CHAR_LIMIT
    assert short["body_truncated"] is False


@pytest.mark.parametrize(("status", "code"), [(404, "not_found"), (401, "forbidden"), (500, "canvas_api_error")])
def test_canvas_errors_become_tool_errors(mock_client, status, code):
    from auth import CanvasAPIError
    from specs.registry import dispatch_tool_call

    mock_client.get_conversation.side_effect = CanvasAPIError("nope", status_code=status)
    mock_client.list_conversations.side_effect = CanvasAPIError("nope", status_code=status)
    assert dispatch_tool_call("get_inbox_conversation", {"conversation_id": "7"})["error"] == code
    assert dispatch_tool_call("list_inbox_conversations", {})["error"] == code


@pytest.mark.parametrize(
    ("argv", "tool", "args"),
    [
        (["inbox", "list"], "list_inbox_conversations", {"scope": "inbox", "course_id": None, "limit": 50}),
        (
            ["inbox", "list", "--scope", "unread", "--course", "123", "--limit", "5"],
            "list_inbox_conversations",
            {"scope": "unread", "course_id": "123", "limit": 5},
        ),
        (["inbox", "show", "42"], "get_inbox_conversation", {"conversation_id": "42"}),
    ],
)
def test_cli_inbox_commands(monkeypatch, argv, tool, args):
    from typer.testing import CliRunner

    from cli import app, bootstrap

    calls = []
    monkeypatch.setattr(bootstrap, "_ensure_auth", lambda: None)
    monkeypatch.setattr(bootstrap, "dispatch_tool_call", lambda name, a: calls.append((name, a)) or {"ok": True})
    result = CliRunner().invoke(app, ["--output", "json", *argv])
    assert result.exit_code == 0, result.output
    assert calls == [(tool, args)]


def test_inbox_tools_are_registered_read_only():
    from specs.registry import TOOL_SPECS

    specs = {spec.name: spec for spec in TOOL_SPECS}
    for name in ("list_inbox_conversations", "get_inbox_conversation"):
        assert specs[name].read_only is True
