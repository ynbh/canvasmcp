from __future__ import annotations

import json
from unittest import mock

import pytest

BACKEND = "https://school.quiz-lti-iad-prod.instructure.com"
API = "https://school.quiz-api-iad-prod.instructure.com"
PARAMS = {
    "backend_url": BACKEND,
    "tool_consumer_instance_guid": "abc123:canvas-lms",
    "custom_canvas_course_id": "5",
    "custom_canvas_assignment_id": "7",
}


def _launch_page(params=None, signature="sig"):
    env = {"ACCOUNT_ID": "1", "NEW_QUIZZES": {"params": params or PARAMS, "signature": signature}}
    return f"<html><script>ENV = {json.dumps(env)};</script></html>"


def _client_with_requester():
    """A real CanvasClient whose Canvas requester is a mock, so tests see the exact requests."""
    from client import CanvasClient

    requester = mock.MagicMock()
    canvas = mock.MagicMock()
    setattr(canvas, "_Canvas__requester", requester)
    patch = mock.patch("client.base.Canvas", return_value=canvas)
    return CanvasClient(base_url="https://canvas.example.test"), requester, patch


def _response(status=200, body=None, text="", headers=None):
    response = mock.Mock(status_code=status, text=text, headers=headers or {})
    response.json.return_value = body
    return response


# -- client: opening a New Quiz -----------------------------------------------------------------------
class TestLaunch:
    def _launch(self, page=None, jwt=None, launch=None):
        client, requester, patch = _client_with_requester()
        session = requester._session
        session.get.return_value = page or _response(text=_launch_page())
        session.post.return_value = jwt or _response(body={"token": "jwt"})
        native = launch or _response(body={"access_token": "lti", "entry_path": {"workflow": "taking", "resourceId": 9}})
        with patch, mock.patch("client.quizzes.requests.post", return_value=native) as post:
            result = client.launch_new_quiz(course_id="5", assignment_id="7")
        return result, session, post

    def test_opens_the_quiz_like_its_canvas_page(self):
        from client.quizzes import NewQuizLaunch

        result, session, post = self._launch()
        assert result == NewQuizLaunch(BACKEND, "lti", "9", "taking")
        get = session.get.call_args
        assert get.args[0] == "https://canvas.example.test/courses/5/assignments/7/launch"
        assert get.kwargs["allow_redirects"] is False
        jwt = session.post.call_args
        assert jwt.args[0] == "https://canvas.example.test/api/v1/jwts"
        assert jwt.kwargs["params"] == {
            "canvas_audience": "false",
            "workflows[]": "new_quizzes_native_launch",
            "context_id": "1",
            "context_type": "account",
        }
        native = post.call_args
        assert native.args[0] == f"{BACKEND}/api/native/launch"
        assert native.kwargs["json"] == {"params": PARAMS, "signature": "sig"}
        assert native.kwargs["headers"] == {"Authorization": "Bearer jwt", "X-Domain": "abc123"}
        assert native.kwargs["allow_redirects"] is False

    def test_makes_exactly_these_requests(self):
        _, session, post = self._launch()
        assert session.get.call_count == 1 and session.post.call_count == 1 and post.call_count == 1
        session.put.assert_not_called()
        session.delete.assert_not_called()
        session.patch.assert_not_called()

    @pytest.mark.parametrize(
        "page",
        [
            _response(text="<html>an ordinary assignment</html>"),
            _response(text=_launch_page(signature="")),
            _response(text=_launch_page({**PARAMS, "custom_canvas_assignment_id": "8"})),
            _response(text=_launch_page({**PARAMS, "custom_canvas_course_id": "6"})),
            _response(text=_launch_page({**PARAMS, "backend_url": "https://evil.example.com"})),
            _response(text=_launch_page({**PARAMS, "backend_url": "http://school.quiz-lti-iad-prod.instructure.com"})),
            _response(status=302),
        ],
    )
    def test_refuses_anything_but_this_new_quiz_before_any_post(self, page):
        from auth import CanvasAPIError

        client, requester, patch = _client_with_requester()
        requester._session.get.return_value = page
        with patch, mock.patch("client.quizzes.requests.post") as post, pytest.raises(CanvasAPIError):
            client.launch_new_quiz(course_id="5", assignment_id="7")
        requester._session.post.assert_not_called()
        post.assert_not_called()

    def test_bad_ids_never_load_a_page(self):
        from auth import CanvasAPIError

        client, requester, patch = _client_with_requester()
        with patch, pytest.raises(CanvasAPIError):
            client.launch_new_quiz(course_id="5", assignment_id="7/../take")
        requester._session.get.assert_not_called()

    def test_a_launch_without_a_session_is_an_error(self):
        from auth import CanvasAPIError

        with pytest.raises(CanvasAPIError):
            self._launch(launch=_response(body={"access_token": "lti", "entry_path": {}}))


# -- client: reading results ---------------------------------------------------------------------------
class TestReader:
    def _reader(self, *responses):
        from client.quizzes import NewQuizLaunch, NewQuizReader

        http = mock.MagicMock()
        http.get.side_effect = list(responses)
        return NewQuizReader(NewQuizLaunch(BACKEND, "lti", "9", "taking"), http=http), http

    def test_reads_attempts_with_the_launch_token(self):
        reader, http = self._reader(_response(body={"attempt_history": []}))
        assert reader.participant_results("9") == {"attempt_history": []}
        call = http.get.call_args
        assert call.args[0] == f"{BACKEND}/api/participant_sessions/9/results"
        assert call.kwargs["headers"]["Authorization"] == "Bearer lti"
        assert call.kwargs["allow_redirects"] is False

    def test_reads_an_attempt_with_its_own_token_and_follows_pages(self):
        results = {"host": API, "token": "signed"}
        reader, http = self._reader(
            _response(body=[{"id": 1}], headers={"X-Last-Evaluated-Hash-Key": "h", "X-Last-Evaluated-Range-Key": "r"}),
            _response(body=[{"id": 2}]),
        )
        assert reader.item_results(results, "4", "6") == [{"id": 1}, {"id": 2}]
        first, second = http.get.call_args_list
        assert first.args[0] == f"{API}/api/quiz_sessions/4/results/6/session_item_results"
        assert first.kwargs["headers"]["Authorization"] == "signed"
        assert first.kwargs["headers"]["AuthType"] == "Signature"
        assert second.kwargs["params"] == {"last_evaluated_hash_key": "h", "last_evaluated_range_key": "r"}

    def test_never_posts(self):
        reader, http = self._reader(_response(body={}), _response(body=[]), _response(body=[]))
        results = {"host": API, "token": "signed"}
        reader.quiz_session(results, "4")
        reader.session_items(results, "4")
        reader.item_results(results, "4", "6")
        assert http.get.call_count == 3
        http.post.assert_not_called()
        http.put.assert_not_called()
        http.patch.assert_not_called()
        http.delete.assert_not_called()

    @pytest.mark.parametrize(
        "path",
        [
            "/api/participant_sessions/9/take",
            "/api/quiz_sessions/4/take",
            "/api/quiz_sessions/4/submit",
            "/api/quiz_sessions/4/autosubmit",
            "/api/quiz_sessions/4/reopen",
            "/api/quiz_sessions/4/record",
            "/api/quiz_sessions/4/session_item_responses/resume_data",
            "/api/participant_sessions/9/results/../take",
            "/api/quiz_sessions/x",
        ],
    )
    def test_only_result_reads_are_allowed(self, path):
        from auth import CanvasAPIError

        reader, http = self._reader()
        with pytest.raises(CanvasAPIError):
            reader._get(API, path, {})
        http.get.assert_not_called()

    @pytest.mark.parametrize(
        "host",
        ["https://evil.example.com", "http://school.quiz-api-iad-prod.instructure.com", "https://canvas.example.test",
         "https://school.quiz-api-iad-prod.instructure.com.evil.example"],
    )
    def test_only_new_quizzes_hosts_are_contacted(self, host):
        from auth import CanvasAPIError

        reader, http = self._reader()
        with pytest.raises(CanvasAPIError):
            reader.quiz_session({"host": host, "token": "signed"}, "4")
        http.get.assert_not_called()

    def test_errors_are_not_followed(self):
        from auth import CanvasAPIError

        redirect = _response(status=302)
        reader, _ = self._reader(redirect)
        with pytest.raises(CanvasAPIError) as raised:
            reader.participant_results("9")
        assert raised.value.status_code == 302
        redirect.close.assert_called_once()


# -- tool ----------------------------------------------------------------------------------------------
ASSIGNMENT = {
    "id": 7,
    "name": "Practice Quiz",
    "points_possible": 3,
    "due_at": "2026-11-14T05:59:59Z",
    "is_quiz_lti_assignment": True,
    "submission": {"attempt": 1, "workflow_state": "graded", "score": 2},
}
OPEN = {
    "can_see_results_page": True,
    "can_see_results_items": True,
    "view_permissions": {"result_view_restricted": False, "attempts_remain": False},
}
ITEMS = [
    {
        "position": 1,
        "points_possible": 1.0,
        "item": {
            "id": "100",
            "item_body": "<p>Pick one</p>",
            "interaction_type": {"slug": "choice"},
            "interaction_data": {
                "choices": [
                    {"id": "b", "item_body": "Beta", "position": 2},
                    {"id": "a", "item_body": "Alpha", "position": 1},
                ]
            },
        },
    },
    {
        "position": 2,
        "points_possible": 1.0,
        "item": {
            "id": "101",
            "item_body": "True?",
            "interaction_type": {"slug": "true-false"},
            "interaction_data": {"true_choice": "True", "false_choice": "False"},
        },
    },
    {
        "position": 3,
        "points_possible": 1.0,
        "stimulus": {"body": "<p>Passage</p>"},
        "item": {"id": "102", "item_body": "Explain", "interaction_type": {"slug": "essay"}, "interaction_data": {}},
    },
]
ITEM_RESULTS = [
    {
        "item_id": "100",
        "score": 0.0,
        "points_possible": 1.0,
        "answer_feedback": {"b": "Not quite"},
        "scored_data": {
            "correct": False,
            "value": {"b": {"user_responded": True, "result_score": 0}, "a": {"user_responded": False, "result_score": 1}},
        },
    },
    {
        "item_id": "101",
        "score": 1.0,
        "points_possible": 1.0,
        "feedback": {"item_feedback": {"neutral": "Right per lecture"}},
        "scored_data": {"correct": True, "value": {"true": {"user_responded": True, "result_score": 1}}},
    },
    {
        "item_id": "102",
        "score": 1.0,
        "points_possible": 1.0,
        "scored_data": {"grade_status": "graded", "value": "<p>Because</p>"},
    },
]


class FakeReader:
    """Stands in for NewQuizReader: two finished attempts unless told otherwise."""

    def __init__(self, launch, *, history=None, entry=None, sessions=None, visibility=OPEN):
        self.launch = launch
        self.history = (
            history
            if history is not None
            else [
                {"id": 31, "percentage": 0.5, "authoritative": False},
                {"id": 32, "percentage": 2 / 3, "authoritative": True},
            ]
        )
        self.entry = entry
        self.sessions = sessions or {}
        self.visibility = visibility
        self.calls: list[tuple] = []

    def participant_results(self, participant_session_id):
        self.calls.append(("participant_results", participant_session_id))
        return {
            "attempt_history": self.history,
            "max_attempts": 2,
            "host": API,
            "token": "signed",
            "quiz_api_quiz_session_id": 400 + int(participant_session_id),
            "participant_session": {**self.visibility, "id": participant_session_id},
        }

    def quiz_session(self, results, quiz_session_id):
        self.calls.append(("quiz_session", quiz_session_id))
        return self.sessions.get(
            quiz_session_id,
            {
                "status": "graded",
                "attempt": 1,
                "start_at": "2026-11-08T01:00:00Z",
                "submitted_at": "2026-11-08T02:00:00Z",
                "quiz": {"title": "Practice Quiz", "instructions": "<p>Do it</p>"},
                "authoritative_result": {"id": "600", "score": 2.0, "points_possible": 3.0, "percentage": 2 / 3},
            },
        )

    def session_items(self, results, quiz_session_id):
        self.calls.append(("session_items", quiz_session_id))
        return list(reversed(ITEMS))

    def item_results(self, results, quiz_session_id, result_id):
        self.calls.append(("item_results", quiz_session_id, result_id))
        return ITEM_RESULTS


@pytest.fixture
def new_quiz(mock_client, monkeypatch):
    from client.quizzes import NewQuizLaunch

    made: list[FakeReader] = []
    options: dict = {}

    def reader(launch):
        made.append(FakeReader(launch, **options))
        return made[-1]

    monkeypatch.setattr("tools.quizzes.NewQuizReader", reader)
    mock_client.get_assignment.return_value = ASSIGNMENT
    mock_client.launch_new_quiz.return_value = NewQuizLaunch(BACKEND, "lti", "33", "taking")

    def run(args=None, **reader_options):
        from tools.quizzes import get_new_quiz_results

        options.clear()
        options.update(reader_options)
        result = get_new_quiz_results({"course_id": "5", "assignment_id": "7", **(args or {})})
        return result, (made[-1] if made else None)

    return run


class TestGetNewQuizResults:
    def test_reads_the_latest_finished_attempt(self, new_quiz, mock_client):
        result, reader = new_quiz()
        mock_client.get_assignment.assert_called_once_with(
            course_id="5", assignment_id="7", include_submission=True, include_discussion_topic=False
        )
        mock_client.launch_new_quiz.assert_called_once_with(course_id="5", assignment_id="7")
        assert result["attempts"] == [
            {"attempt": 1, "percentage": 50.0, "kept": False},
            {"attempt": 2, "percentage": 66.7, "kept": True},
        ]
        assert result["attempt"] == 2 and result["score"] == 2.0 and result["attempt_points_possible"] == 3.0
        assert result["instructions"] == "<p>Do it</p>" and result["allowed_attempts"] == 2
        assert ("participant_results", "32") in reader.calls
        assert ("item_results", "432", "600") in reader.calls
        assert "hidden_by_quiz_settings" not in result

    def test_maps_each_question_type(self, new_quiz):
        result, _ = new_quiz()
        choice, true_false, essay = result["questions"]
        assert choice["question"] == "<p>Pick one</p>"
        assert choice["choices"] == ["Alpha", "Beta"]
        assert choice["your_answer"] == "Beta" and choice["result"] is False and choice["points"] == 0.0
        assert choice["correct_answers"] == ["Alpha"] and choice["feedback"] == ["Not quite"]
        assert true_false["your_answer"] == "True" and true_false["correct_answers"] == ["True"]
        assert true_false["choices"] is None and true_false["feedback"] == ["Right per lecture"]
        assert essay["your_answer"] == "<p>Because</p>" and essay["passage"] == "<p>Passage</p>"
        assert essay["grade_status"] == "graded" and essay["correct_answers"] is None

    def test_reads_an_earlier_attempt(self, new_quiz):
        result, reader = new_quiz({"attempt": 1})
        assert result["attempt"] == 1
        assert ("participant_results", "31") in reader.calls and ("participant_results", "32") not in reader.calls

    def test_an_attempt_past_the_last_finished_one_is_refused(self, new_quiz):
        result, reader = new_quiz({"attempt": 3})
        assert result["error"] == "invalid_argument"
        assert not any(call[0] == "quiz_session" for call in reader.calls)

    def test_nothing_is_opened_until_canvas_shows_a_submitted_attempt(self, new_quiz, mock_client):
        for submission in ({}, {"attempt": 0, "workflow_state": "unsubmitted"}, {"attempt": 1, "workflow_state": "unsubmitted"}):
            mock_client.get_assignment.return_value = {**ASSIGNMENT, "submission": submission}
            result, _ = new_quiz()
            assert result["message"] == "No finished attempt to show yet."
        mock_client.launch_new_quiz.assert_not_called()

    def test_a_classic_quiz_points_to_get_quiz_results(self, new_quiz, mock_client):
        mock_client.get_assignment.return_value = {"id": 7, "quiz_id": 70, "is_quiz_lti_assignment": False}
        result, _ = new_quiz()
        assert result["error"] == "invalid_argument" and "quiz_id 70" in result["message"]
        mock_client.get_assignment.return_value = {"id": 7}
        assert new_quiz()[0]["error"] == "invalid_argument"
        mock_client.launch_new_quiz.assert_not_called()

    @pytest.mark.parametrize(
        "session",
        [
            {"status": "in_progress", "attempt": 2, "submitted_at": None},
            {"status": "pending", "attempt": 2, "submitted_at": None},
            {"status": "graded", "attempt": 2, "submitted_at": None},
        ],
    )
    def test_an_unfinished_attempt_is_never_read(self, new_quiz, session):
        result, reader = new_quiz(sessions={"432": session})
        assert result["message"] == "This attempt isn't finished, so nothing in it is read."
        assert "questions" not in result
        assert not any(call[0] in ("session_items", "item_results") for call in reader.calls)

    def test_a_finished_attempt_missing_from_the_history_is_still_read(self, new_quiz):
        # New Quizzes can leave the current record "in progress" with an empty history after a submission.
        result, reader = new_quiz(history=[])
        assert reader.calls[0] == ("participant_results", "33")
        assert ("quiz_session", "433") in reader.calls
        assert result["attempts"] == [{"attempt": 1, "percentage": 66.7, "kept": True}]
        assert result["question_count"] == 3

    def test_when_questions_are_hidden_only_the_score_is_shown(self, new_quiz):
        result, reader = new_quiz(visibility={**OPEN, "can_see_results_items": False})
        assert result["score"] == 2.0 and "questions" not in result
        assert result["message"].startswith("New Quizzes doesn't show you this attempt's questions")
        assert not any(call[0] in ("session_items", "item_results") for call in reader.calls)

    def test_settings_the_instructor_turned_off_stay_off(self, new_quiz):
        flags = {
            "result_view_restricted": False,
            "display_items": True,
            "display_item_response": True,
            "display_points_awarded": True,
            "display_item_response_correctness": False,
            "display_item_correct_answer": False,
            "display_item_response_qualifier": "always",
        }
        result, _ = new_quiz(visibility={**OPEN, "view_permissions": flags})
        choice = result["questions"][0]
        assert choice["your_answer"] == "Beta" and choice["points"] == 0.0
        assert "result" not in choice and "correct_answers" not in choice
        assert result["hidden_by_quiz_settings"] == ["correctness", "correct answers"]

    def test_restricted_results_show_only_what_is_listed(self, new_quiz):
        flags = {"result_view_restricted": True, "display_items": True}
        result, _ = new_quiz(visibility={**OPEN, "view_permissions": flags})
        choice = result["questions"][0]
        assert result["score"] is None
        assert set(choice) == {"position", "type", "question", "passage", "choices", "points_possible"}

    def test_answers_shown_only_after_the_last_attempt_wait_for_it(self, new_quiz):
        flags = {
            "result_view_restricted": True,
            "display_items": True,
            "display_item_response": True,
            "display_item_response_qualifier": "after_last_attempt",
            "attempts_remain": True,
        }
        result, _ = new_quiz(visibility={**OPEN, "view_permissions": flags})
        assert "your_answer" not in result["questions"][0]
        flags["attempts_remain"] = False
        result, _ = new_quiz(visibility={**OPEN, "view_permissions": flags})
        assert result["questions"][0]["your_answer"] == "Beta"

    def test_answers_outside_their_show_window_are_hidden(self, new_quiz):
        flags = {"result_view_restricted": False, "hide_item_responses_at": "2020-01-01T00:00:00Z"}
        result, _ = new_quiz(visibility={**OPEN, "view_permissions": flags})
        assert "your_answer" not in result["questions"][0]


@pytest.mark.parametrize(
    ("args", "error"),
    [
        ({"course_id": "5"}, "missing_argument"),
        ({"course_id": "5", "assignment_id": "7/../take"}, "invalid_argument"),
        ({"course_id": "5", "assignment_id": "7", "attempt": 0}, "invalid_argument"),
    ],
)
def test_bad_arguments_never_reach_canvas(mock_client, args, error):
    from specs.registry import dispatch_tool_call

    assert dispatch_tool_call("get_new_quiz_results", args)["error"] == error
    assert mock_client.mock_calls == []


def test_new_quiz_results_is_read_only():
    from specs.registry import TOOL_SPECS

    assert {spec.name: spec for spec in TOOL_SPECS}["get_new_quiz_results"].read_only is True
