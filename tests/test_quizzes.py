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


# -- client: nothing but reads -------------------------------------------------------------------------
class TestQuizClientOnlyReads:
    def test_every_api_call_is_a_get(self):
        client, requester, patch = _client_with_requester()
        requester.request.return_value.json.return_value = {"quiz_submissions": [], "submission_history": []}
        with patch, mock.patch("client.base.PaginatedList", return_value=[]) as paginated:
            client.list_quizzes(course_id="1")
            client.get_quiz(course_id="1", quiz_id="2")
            client.list_quiz_submissions(course_id="1", quiz_id="2")
            client.list_submission_questions(course_id="1", quiz_id="2", quiz_submission_id="3", attempt=1)
            client.get_submission_history(course_id="1", assignment_id="4")
        assert requester.request.call_args_list and all(c.args[0] == "GET" for c in requester.request.call_args_list)
        assert paginated.call_args_list and all(c.args[2] == "GET" for c in paginated.call_args_list)
        endpoints = [c.args[1] for c in requester.request.call_args_list] + [c.args[3] for c in paginated.call_args_list]
        assert not any("take" in e or "/start" in e for e in endpoints)
        requester._session.post.assert_not_called()
        requester._session.put.assert_not_called()

    def test_questions_are_read_for_one_attempt(self):
        client, _, patch = _client_with_requester()
        with patch, mock.patch("client.base.PaginatedList", return_value=[]) as paginated:
            client.list_submission_questions(course_id="1", quiz_id="2", quiz_submission_id="3", attempt=2)
        sent = paginated.call_args.kwargs["_kwargs"]
        assert ("quiz_submission_id", "3") in sent and ("quiz_submission_attempt", 2) in sent

    def test_review_page_is_a_get_without_redirects(self):
        client, requester, patch = _client_with_requester()
        requester._session.get.return_value = mock.Mock(status_code=200, text="<html></html>")
        with patch:
            html = client.get_quiz_review_page(course_id="1", quiz_id="2", quiz_submission_id="3", attempt=1)
        assert html == "<html></html>"
        call = requester._session.get.call_args
        assert call.args[0] == "https://canvas.example.test/courses/1/quizzes/2/history"
        assert call.kwargs["allow_redirects"] is False
        assert call.kwargs["params"] == {"quiz_submission_id": "3", "version": 1}

    def test_review_page_redirect_is_an_error_not_followed(self):
        from auth import CanvasAPIError

        client, requester, patch = _client_with_requester()
        requester._session.get.return_value = mock.Mock(status_code=302, text="")
        with patch, pytest.raises(CanvasAPIError) as raised:
            client.get_quiz_review_page(course_id="1", quiz_id="2", quiz_submission_id="3", attempt=1)
        assert raised.value.status_code == 302
        assert requester._session.get.call_count == 1
        requester._session.get.return_value.close.assert_called_once()

    def test_only_review_pages_can_be_loaded(self):
        from client.quizzes import _REVIEW_PATH

        assert _REVIEW_PATH.fullmatch("/courses/1/quizzes/2/history")
        for path in ("/courses/1/quizzes/2/take", "/courses/1/quizzes/2", "/courses/1/quizzes/2/history/take",
                     "/courses/1/quizzes/2/submissions", "/courses/x/quizzes/2/history"):
            assert not _REVIEW_PATH.fullmatch(path)

    def test_bad_ids_never_reach_the_review_page(self):
        from auth import CanvasAPIError

        client, requester, patch = _client_with_requester()
        with patch, pytest.raises(CanvasAPIError):
            client.get_quiz_review_page(course_id="1/../take", quiz_id="2", quiz_submission_id="3", attempt=1)
        requester._session.get.assert_not_called()


# -- list_course_quizzes -------------------------------------------------------------------------------
QUIZ = {
    "id": 10, "assignment_id": 100, "title": "Quiz 1", "quiz_type": "assignment", "points_possible": 5,
    "question_count": 3, "time_limit": 10, "allowed_attempts": 2, "due_at": "2026-10-20T04:59:00Z",
    "unlock_at": None, "lock_at": None, "published": True, "locked_for_user": False, "show_correct_answers": True,
    "has_access_code": False, "require_lockdown_browser": False, "one_question_at_a_time": True,
    "cant_go_back": True, "scoring_policy": "keep_highest",
}


class TestListCourseQuizzes:
    def test_maps_settings_and_your_status(self, mock_client):
        from tools.quizzes import list_course_quizzes

        mock_client.list_quizzes.return_value = [QUIZ, {**QUIZ, "id": 11, "assignment_id": None,
                                                        "quiz_type": "practice_quiz", "allowed_attempts": -1}]
        mock_client.list_assignments.return_value = [
            {"id": 100, "submission": {"workflow_state": "graded", "score": 4, "attempt": 1}},
            {"id": 200, "name": "Vocab quiz", "is_quiz_lti_assignment": True, "points_possible": 10,
             "due_at": "2026-10-21T04:59:00Z", "allowed_attempts": 1, "submission": {"workflow_state": "unsubmitted"}},
        ]
        result = list_course_quizzes({"course_id": "5"})
        graded, practice, new = result["quizzes"]
        assert graded["time_limit_minutes"] == 10 and graded["type"] == "graded quiz"
        assert graded["one_question_at_a_time"] and graded["cant_go_back"]
        assert graded["your_status"] == {"state": "graded", "score": 4, "submitted_at": None, "attempts_used": 1,
                                         "attempts_left": 1, "late": None, "missing": None}
        assert practice["allowed_attempts"] == "unlimited" and practice["your_status"] is None
        assert new["kind"] == "new_quiz" and "allowed_attempts" not in new
        assert new["your_status"]["attempts_left"] is None   # the real limit lives inside the New Quizzes app
        assert mock_client.list_assignments.call_args.kwargs["include_submission"] is True
        assert any("never" in n.lower() or "nothing" in n.lower() for n in result["notes"])

    def test_hidden_quizzes_page_still_lists_new_quizzes(self, mock_client):
        from auth import CanvasAPIError
        from tools.quizzes import list_course_quizzes

        mock_client.list_quizzes.side_effect = CanvasAPIError("hidden", status_code=404)
        mock_client.list_assignments.return_value = [{"id": 200, "name": "NQ", "is_quiz_lti_assignment": True}]
        result = list_course_quizzes({"course_id": "5"})
        assert [q["kind"] for q in result["quizzes"]] == ["new_quiz"]
        mock_client.get_quiz.assert_not_called()

    def test_hidden_quizzes_page_finds_classic_quizzes_through_assignments(self, mock_client):
        from auth import CanvasAPIError
        from tools.quizzes import list_course_quizzes

        mock_client.list_quizzes.side_effect = CanvasAPIError("hidden", status_code=404)
        mock_client.list_assignments.return_value = [
            {"id": 100, "name": "Lab 5 - Quiz", "quiz_id": 10, "submission_types": ["online_quiz"],
             "submission": {"workflow_state": "graded", "score": 10, "attempt": 1}},
            {"id": 101, "name": "Lab 5", "submission_types": ["online_upload"]},
        ]
        mock_client.get_quiz.return_value = QUIZ
        result = list_course_quizzes({"course_id": "5"})
        (quiz,) = result["quizzes"]
        assert quiz["kind"] == "classic_quiz" and quiz["quiz_id"] == "10"
        assert quiz["your_status"]["score"] == 10 and quiz["time_limit_minutes"] == 10
        mock_client.get_quiz.assert_called_once_with(course_id="5", quiz_id="10")
        assert any("found through" in n for n in result["notes"])

    @pytest.mark.parametrize("status", [401, 403, 404])
    def test_hidden_page_status_codes_and_unreadable_quizzes(self, mock_client, status):
        from auth import CanvasAPIError
        from tools.quizzes import list_course_quizzes

        mock_client.list_quizzes.side_effect = CanvasAPIError("hidden", status_code=status)
        mock_client.list_assignments.return_value = [
            {"id": 100, "quiz_id": 10, "submission_types": ["online_quiz"]},
            {"id": 101, "quiz_id": 11, "submission_types": ["online_quiz"]},
        ]
        mock_client.get_quiz.side_effect = [CanvasAPIError("locked", status_code=403), QUIZ]
        result = list_course_quizzes({"course_id": "5"})
        assert [q["quiz_id"] for q in result["quizzes"]] == ["10"]   # QUIZ's own id; the unreadable one is skipped
        assert any("wouldn't show 1" in n and "10" in n for n in result["notes"])

    def test_other_errors_still_surface(self, mock_client):
        from auth import CanvasAPIError
        from tools.quizzes import list_course_quizzes

        mock_client.list_quizzes.side_effect = CanvasAPIError("down", status_code=500)
        with pytest.raises(CanvasAPIError):
            list_course_quizzes({"course_id": "5"})

    def test_rejects_a_course_id_that_is_not_a_canvas_id(self, mock_client):
        from tools.quizzes import list_course_quizzes

        assert list_course_quizzes({"course_id": "1/take"})["error"] == "invalid_argument"
        assert mock_client.mock_calls == []


# -- get_quiz_results ----------------------------------------------------------------------------------
MC = {"id": 1, "position": 1, "question_type": "multiple_choice_question", "question_text": "<p>2+2?</p>",
      "answers": [{"id": 11, "text": "3"}, {"id": 12, "text": "4"}]}
MA = {"id": 2, "position": 2, "question_type": "multiple_answers_question", "question_text": "Primes?",
      "answers": [{"id": 21, "text": "2"}, {"id": 22, "text": "4"}, {"id": 23, "text": "5"}]}
MATCH = {"id": 3, "position": 3, "question_type": "matching_question", "question_text": "Match",
         "answers": [{"id": 31, "text": "TCP"}], "matches": [{"match_id": 91, "text": "reliable"}]}
BLANKS = {"id": 4, "position": 4, "question_type": "fill_in_multiple_blanks_question", "question_text": "[a] [b]",
          "answers": [{"id": 41, "text": "x"}, {"id": 42, "text": "y"}]}
DATA = [
    {"question_id": 1, "correct": False, "points": 0, "answer_id": 11, "text": ""},
    {"question_id": 2, "correct": "partial", "points": 0.5, "answer_21": "1", "answer_22": "1", "answer_23": "0"},
    {"question_id": 3, "correct": True, "points": 1, "answer_31": "91"},
    {"question_id": 4, "correct": False, "points": 0, "answer_for_a": "w", "answer_for_b": "y"},
]
REVIEW = """<div class="question multiple_choice_question" id="question_1">
  <div class="answer answer_for_ wrong_answer selected_answer" id="answer_11"><div class="answer_text">3</div></div>
  <div class="answer answer_for_ correct_answer" id="answer_12"><div class="answer_text">4</div></div></div>
<div class="question" id="question_2">
  <div class="answer correct_answer selected_answer" id="answer_21"><span>2</span></div>
  <div class="answer selected_answer" id="answer_22"><span>4</span></div>
  <div class="answer correct_answer" id="answer_23"><span>5</span></div></div>
<div class="question" id="question_4">
  <div class="answer correct_answer" id="answer_41"><span>x</span></div>
  <div class="answer correct_answer" id="answer_42"><span>y</span></div></div>"""


def _finished(mock_client, *, state="complete", attempt=1, show_correct=True, hide_results=None):
    mock_client.get_quiz.return_value = {"id": 10, "assignment_id": 100, "title": "Quiz 1", "quiz_type": "assignment",
                                         "show_correct_answers": show_correct, "hide_results": hide_results,
                                         "allowed_attempts": 2, "time_limit": 10}
    mock_client.list_quiz_submissions.return_value = [
        {"id": 77, "attempt": attempt, "workflow_state": state, "score": 1.5, "kept_score": 1.5, "time_spent": 300,
         "started_at": "2026-10-01T10:00:00Z", "finished_at": "2026-10-01T10:05:00Z"}]
    mock_client.get_submission_history.return_value = [
        {"attempt": 1, "score": 1.5, "workflow_state": "graded", "submission_data": DATA}]
    mock_client.list_submission_questions.return_value = [BLANKS, MATCH, MA, MC]
    mock_client.get_quiz_review_page.return_value = REVIEW


class TestGetQuizResults:
    def test_reads_a_finished_attempt_question_by_question(self, mock_client):
        from tools.quizzes import get_quiz_results

        _finished(mock_client)
        r = get_quiz_results({"course_id": "5", "quiz_id": "10"})
        assert r["attempt"] == 1 and r["score"] == 1.5 and r["question_count"] == 4
        assert r["attempts"][0]["minutes_spent"] == 5.0
        q1, q2, q3, q4 = r["questions"]
        assert q1["your_answer"] == "3" and q1["result"] is False
        assert q1["correct_answers"] == ["4"] and q1["correct_answers_source"] == "review_page"
        assert q2["your_answer"] == ["2", "4"] and q2["result"] == "partial" and q2["correct_answers"] == ["2", "5"]
        assert q3["your_answer"] == {"TCP": "reliable"} and q3["correct_answers_source"] == "your_correct_answer"
        assert q4["your_answer"] == {"a": "w", "b": "y"} and q4["correct_answers"] == ["x", "y"]
        kwargs = mock_client.list_submission_questions.call_args.kwargs
        assert kwargs["quiz_submission_id"] == "77" and kwargs["attempt"] == 1

    def test_nothing_is_read_while_an_attempt_is_in_progress(self, mock_client):
        from tools.quizzes import get_quiz_results

        _finished(mock_client, state="untaken", attempt=2)
        r = get_quiz_results({"course_id": "5", "quiz_id": "10"})
        assert "in progress" in r["message"] and "questions" not in r
        mock_client.list_submission_questions.assert_not_called()
        mock_client.get_quiz_review_page.assert_not_called()

    def test_untaken_quiz_reads_nothing_more(self, mock_client):
        from tools.quizzes import get_quiz_results

        _finished(mock_client)
        mock_client.list_quiz_submissions.return_value = []
        mock_client.get_submission_history.return_value = []
        r = get_quiz_results({"course_id": "5", "quiz_id": "10"})
        assert r["message"] == "No finished attempt to show yet." and r["attempts"] == []
        mock_client.list_submission_questions.assert_not_called()
        mock_client.get_quiz_review_page.assert_not_called()

    def test_hidden_results_show_scores_only(self, mock_client):
        from tools.quizzes import get_quiz_results

        _finished(mock_client, hide_results="always")
        r = get_quiz_results({"course_id": "5", "quiz_id": "10"})
        assert r["attempts"][0]["score"] == 1.5 and "questions" not in r
        mock_client.list_submission_questions.assert_not_called()

    def test_no_review_page_when_correct_answers_are_hidden(self, mock_client):
        from tools.quizzes import get_quiz_results

        _finished(mock_client, show_correct=False)
        r = get_quiz_results({"course_id": "5", "quiz_id": "10"})
        mock_client.get_quiz_review_page.assert_not_called()
        q1 = r["questions"][0]
        assert q1["correct_answers"] is None and q1["your_answer"] == "3"

    def test_review_page_failure_still_returns_your_results(self, mock_client):
        from auth import CanvasAPIError
        from tools.quizzes import get_quiz_results

        _finished(mock_client)
        mock_client.get_quiz_review_page.side_effect = CanvasAPIError("redirect", status_code=302)
        r = get_quiz_results({"course_id": "5", "quiz_id": "10"})
        assert "review_page" in r and r["questions"][0]["your_answer"] == "3"

    def test_unfinished_attempt_numbers_are_refused(self, mock_client):
        from tools.quizzes import get_quiz_results

        _finished(mock_client)
        assert get_quiz_results({"course_id": "5", "quiz_id": "10", "attempt": 2}) == {
            "error": "invalid_argument",
            "message": "attempt 2 isn't a finished attempt",
        }
        mock_client.list_submission_questions.assert_not_called()
        mock_client.get_quiz_review_page.assert_not_called()

    @pytest.mark.parametrize("ids", [{"course_id": "5", "quiz_id": "10/take"}, {"course_id": "../5", "quiz_id": "10"}])
    def test_ids_that_are_not_canvas_ids_never_reach_canvas(self, mock_client, ids):
        from tools.quizzes import get_quiz_results

        assert get_quiz_results(ids)["error"] == "invalid_argument"
        assert mock_client.mock_calls == []


def test_instructions_in_list_and_results(mock_client):
    from tools.quizzes import get_quiz_results, list_course_quizzes

    _finished(mock_client)
    mock_client.get_quiz.return_value["description"] = "<p>Chapters 1-3. Notes allowed.</p>"
    assert get_quiz_results({"course_id": "5", "quiz_id": "10"})["instructions"] == "<p>Chapters 1-3. Notes allowed.</p>"
    mock_client.list_quizzes.return_value = [{**QUIZ, "description": "<p>Notes allowed.</p>"}, QUIZ]
    mock_client.list_assignments.return_value = []
    with_text, without = list_course_quizzes({"course_id": "5"})["quizzes"]
    assert with_text["instructions"] == "<p>Notes allowed.</p>" and without["instructions"] is None


def test_canvas_errors_become_tool_errors(mock_client):
    from auth import CanvasAPIError
    from specs.registry import dispatch_tool_call

    mock_client.get_quiz.side_effect = CanvasAPIError("nope", status_code=401)
    mock_client.list_quizzes.side_effect = CanvasAPIError("nope", status_code=500)
    assert dispatch_tool_call("get_quiz_results", {"course_id": "5", "quiz_id": "10"})["error"] == "forbidden"
    assert dispatch_tool_call("list_course_quizzes", {"course_id": "5"})["error"] == "canvas_api_error"


@pytest.mark.parametrize(
    ("argv", "tool", "args"),
    [
        (["quizzes", "list", "5"], "list_course_quizzes", {"course_id": "5", "limit": 100}),
        (["quizzes", "results", "5", "10"], "get_quiz_results", {"course_id": "5", "quiz_id": "10", "attempt": None}),
        (["quizzes", "results", "5", "10", "--attempt", "2"], "get_quiz_results",
         {"course_id": "5", "quiz_id": "10", "attempt": 2}),
    ],
)
def test_cli_quiz_commands(monkeypatch, argv, tool, args):
    from typer.testing import CliRunner

    from cli import app, output as cli_output

    calls = []
    monkeypatch.setattr(cli_output, "_ensure_auth", lambda: None)
    monkeypatch.setattr(cli_output, "dispatch_tool_call", lambda name, a: calls.append((name, a)) or {"ok": True})
    result = CliRunner().invoke(app, ["--output", "json", *argv])
    assert result.exit_code == 0, result.output
    assert calls == [(tool, args)]
