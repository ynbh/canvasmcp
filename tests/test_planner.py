from __future__ import annotations

from unittest import mock

import pytest


def _client_with_requester():
    """A real CanvasClient whose Canvas requester is a mock, so tests see the exact requests."""
    from client import CanvasClient

    requester = mock.MagicMock()
    canvas = mock.MagicMock()
    setattr(canvas, "_Canvas__requester", requester)
    patch = mock.patch("client.base.Canvas", return_value=canvas)
    return CanvasClient(base_url="https://canvas.example.test"), requester, patch


# -- client: writes only touch your own planner -------------------------------------------------------
class TestPlannerClient:
    def test_each_call_uses_only_its_planner_endpoint(self):
        client, requester, patch = _client_with_requester()
        requester.request.return_value.json.return_value = {"id": 1}
        with patch, mock.patch("client.base.PaginatedList", return_value=[]) as paginated:
            client.list_planner_items(start_date="2026-10-01", end_date="2026-10-31", incomplete_only=True)
            client.list_planner_overrides()
            client.get_planner_note(note_id="7")
            client.create_planner_note(fields={"title": "Read ch. 3", "todo_date": "2026-10-12"})
            client.update_planner_note(note_id="7", fields={"title": "Read ch. 4"})
            client.delete_planner_note(note_id="7")
            client.create_planner_override(plannable_type="assignment", plannable_id="9", state={"marked_complete": "true"})
            client.update_planner_override(override_id="3", state={"marked_complete": "false"})
        calls = [(c.args[0], c.args[1]) for c in requester.request.call_args_list]
        assert calls == [
            ("GET", "planner_notes/7"),
            ("POST", "planner_notes"),
            ("PUT", "planner_notes/7"),
            ("DELETE", "planner_notes/7"),
            ("POST", "planner/overrides"),
            ("PUT", "planner/overrides/3"),
        ]
        assert [(c.args[2], c.args[3]) for c in paginated.call_args_list] == [("GET", "planner/items"), ("GET", "planner/overrides")]
        items_params = paginated.call_args_list[0].kwargs["_kwargs"]
        assert ("filter", "incomplete_items") in items_params and ("start_date", "2026-10-01") in items_params

    def test_fields_are_sent_as_given(self):
        client, requester, patch = _client_with_requester()
        requester.request.return_value.json.return_value = {}
        with patch:
            client.create_planner_note(fields={"title": "Read ch. 3", "details": "pp. 40-60", "course_id": "5"})
            client.create_planner_override(plannable_type="quiz", plannable_id="9", state={"marked_complete": "true"})
        note, override = (c.kwargs["_kwargs"] for c in requester.request.call_args_list)
        assert set(note) == {("title", "Read ch. 3"), ("details", "pp. 40-60"), ("course_id", "5")}
        assert set(override) == {("plannable_type", "quiz"), ("plannable_id", "9"), ("marked_complete", "true")}


# -- tools ---------------------------------------------------------------------------------------------
NOTE = {"id": 7, "title": "Read ch. 3", "description": "pp. 40-60", "todo_date": "2026-10-12T05:00:00Z",
        "course_id": 5, "workflow_state": "active"}


class TestTodoNotes:
    def test_create(self, mock_client):
        from tools.planner import create_todo_note

        mock_client.create_planner_note.return_value = NOTE
        r = create_todo_note({"title": "  Read ch. 3 ", "details": "pp. 40-60", "todo_date": "2026-10-12", "course_id": "5"})
        assert r["created"] and r["note"] == {"note_id": "7", "title": "Read ch. 3", "details": "pp. 40-60",
                                              "todo_date": "2026-10-12T05:00:00Z", "course_id": "5", "state": "active"}
        assert mock_client.create_planner_note.call_args.kwargs["fields"] == {
            "title": "Read ch. 3", "details": "pp. 40-60", "todo_date": "2026-10-12", "course_id": "5"}

    @pytest.mark.parametrize(("args", "message"), [
        ({"title": "x" * 256}, "title must be at most 255 characters"),
        ({"title": "ok", "details": "x" * 10001}, "details must be at most 10000 characters"),
        ({"title": "ok", "todo_date": "next tuesday"},
         "todo_date must be a date (YYYY-MM-DD) or ISO date-time: not a date: 'next tuesday'"),
        ({"title": "ok", "course_id": "../5"}, "course_id must be a Canvas ID"),
    ])
    def test_create_rejects_bad_input(self, mock_client, args, message):
        from specs.registry import dispatch_tool_call

        assert dispatch_tool_call("create_todo_note", args) == {"error": "invalid_argument", "message": message}
        assert mock_client.mock_calls == []

    def test_update_changes_only_what_is_given(self, mock_client):
        from tools.planner import update_todo_note

        mock_client.update_planner_note.return_value = {**NOTE, "todo_date": "2026-10-15T05:00:00Z"}
        r = update_todo_note({"note_id": "7", "todo_date": "2026-10-15"})
        assert r["updated"] and r["note"]["todo_date"] == "2026-10-15T05:00:00Z"
        assert mock_client.update_planner_note.call_args.kwargs == {"note_id": "7", "fields": {"todo_date": "2026-10-15"}}

    @pytest.mark.parametrize(("args", "message"), [
        ({"note_id": "7/../8", "title": "x"}, "note_id must be a Canvas ID"),
        ({"note_id": "7"}, "give at least one of title, details, todo_date, course_id to change"),
        ({"note_id": "7", "title": None}, "give at least one of title, details, todo_date, course_id to change"),
        ({"note_id": "7", "title": " "}, "title can't be blank"),
    ])
    def test_update_needs_a_canvas_id_and_a_change(self, mock_client, args, message):
        from specs.registry import dispatch_tool_call

        assert dispatch_tool_call("update_todo_note", args) == {"error": "invalid_argument", "message": message}
        assert mock_client.mock_calls == []

    def test_delete_refuses_an_id_that_is_not_a_canvas_id(self, mock_client):
        from specs.registry import dispatch_tool_call

        assert dispatch_tool_call("delete_todo_note", {"note_id": "7/../8"})["error"] == "invalid_argument"
        assert mock_client.mock_calls == []

    def test_delete_reads_the_note_first(self, mock_client):
        from tools.planner import delete_todo_note

        mock_client.get_planner_note.return_value = NOTE
        r = delete_todo_note({"note_id": "7"})
        assert r["deleted"] and r["note"]["title"] == "Read ch. 3"
        mock_client.delete_planner_note.assert_called_once_with(note_id="7")

    def test_delete_stops_if_the_note_cannot_be_read(self, mock_client):
        from auth import CanvasAPIError
        from specs.registry import dispatch_tool_call

        mock_client.get_planner_note.side_effect = CanvasAPIError("nope", status_code=404)
        assert dispatch_tool_call("delete_todo_note", {"note_id": "7"})["error"] == "not_found"
        mock_client.delete_planner_note.assert_not_called()


class TestTodoItemState:
    def test_marks_done_with_a_new_override(self, mock_client):
        from tools.planner import set_todo_item_state

        mock_client.list_planner_overrides.return_value = [{"id": 1, "plannable_type": "quiz", "plannable_id": 9}]
        mock_client.create_planner_override.return_value = {"marked_complete": True, "dismissed": False}
        r = set_todo_item_state({"plannable_type": "assignment", "plannable_id": "9", "done": True})
        assert r["done"] is True
        mock_client.create_planner_override.assert_called_once_with(
            plannable_type="assignment", plannable_id="9", state={"marked_complete": "true"})
        mock_client.update_planner_override.assert_not_called()

    def test_updates_an_existing_override(self, mock_client):
        from tools.planner import set_todo_item_state

        mock_client.list_planner_overrides.return_value = [{"id": 4, "plannable_type": "assignment", "plannable_id": 9}]
        mock_client.update_planner_override.return_value = {"marked_complete": False, "dismissed": True}
        r = set_todo_item_state({"plannable_type": "assignment", "plannable_id": "9", "done": False, "dismissed": True})
        assert r["done"] is False and r["dismissed"] is True
        mock_client.update_planner_override.assert_called_once_with(
            override_id="4", state={"marked_complete": "false", "dismissed": "true"})
        mock_client.create_planner_override.assert_not_called()

    @pytest.mark.parametrize("args", [
        {"plannable_type": "submission", "plannable_id": "9", "done": True},
        {"plannable_type": "assignment", "plannable_id": "9/../1", "done": True},
        {"plannable_type": "assignment", "plannable_id": "9"},
        {"plannable_type": "assignment", "plannable_id": "9", "done": None},
        {"plannable_type": "assignment", "plannable_id": "9", "done": "yes"},
    ])
    def test_rejects_bad_input(self, mock_client, args):
        from specs.registry import dispatch_tool_call

        assert dispatch_tool_call("set_todo_item_state", args)["error"] == "invalid_argument"
        assert mock_client.mock_calls == []

    def test_sends_canvas_boolean_strings(self, mock_client):
        from tools.planner import set_todo_item_state

        mock_client.list_planner_overrides.return_value = []
        mock_client.create_planner_override.return_value = {"marked_complete": False, "dismissed": False}
        set_todo_item_state({"plannable_type": "planner_note", "plannable_id": "7", "done": False, "dismissed": False})
        assert mock_client.create_planner_override.call_args.kwargs["state"] == {
            "marked_complete": "false", "dismissed": "false"}


def test_list_planner_items_maps_items(mock_client):
    from tools.planner import list_planner_items

    mock_client.list_planner_items.return_value = [
        {"plannable_type": "assignment", "plannable_id": 9, "plannable": {"title": "HW 3"}, "course_id": 5,
         "plannable_date": "2026-10-12T04:59:00Z", "context_name": "OS", "submissions": {"submitted": False},
         "planner_override": {"marked_complete": True}},
        {"plannable_type": "planner_note", "plannable_id": 7, "plannable": {"title": "Read", "details": "pp. 1-9"}},
    ]
    r = list_planner_items({"start_date": "2026-10-01", "incomplete_only": True})
    hw, note = r["items"]
    assert hw["done"] is True and hw["submitted"] is False and hw["title"] == "HW 3" and hw["details"] is None
    assert note["details"] == "pp. 1-9" and note["done"] is False
    assert mock_client.list_planner_items.call_args.kwargs["incomplete_only"] is True
    sent = mock_client.list_planner_items.call_args.kwargs
    assert sent == {"start_date": "2026-10-01", "end_date": None, "incomplete_only": True, "limit": 100}
    assert list_planner_items({"end_date": "soon"})["error"] == "invalid_argument"
    assert mock_client.list_planner_items.call_count == 1


@pytest.mark.parametrize(
    ("argv", "tool", "args"),
    [
        (["planner", "items", "--incomplete"], "list_planner_items",
         {"start_date": None, "end_date": None, "incomplete_only": True, "limit": 100}),
        (["planner", "add", "Read ch. 3", "--date", "2026-10-12"], "create_todo_note",
         {"title": "Read ch. 3", "todo_date": "2026-10-12", "details": None, "course_id": None}),
        (["planner", "edit", "7", "--title", "Read ch. 4"], "update_todo_note",
         {"note_id": "7", "title": "Read ch. 4", "todo_date": None, "details": None, "course_id": None}),
        (["planner", "delete", "7"], "delete_todo_note", {"note_id": "7"}),
        (["planner", "done", "assignment", "9"], "set_todo_item_state",
         {"plannable_type": "assignment", "plannable_id": "9", "done": True}),
        (["planner", "done", "assignment", "9", "--undo"], "set_todo_item_state",
         {"plannable_type": "assignment", "plannable_id": "9", "done": False}),
    ],
)
def test_cli_planner_commands(monkeypatch, argv, tool, args):
    from typer.testing import CliRunner

    from cli import app, output as cli_output

    calls = []
    monkeypatch.setattr(cli_output, "_ensure_auth", lambda: None)
    monkeypatch.setattr(cli_output, "dispatch_tool_call", lambda name, a: calls.append((name, a)) or {"ok": True})
    result = CliRunner().invoke(app, ["--output", "json", *argv])
    assert result.exit_code == 0, result.output
    assert calls == [(tool, args)]
