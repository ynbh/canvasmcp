from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

import requests
from canvasapi import Canvas
from canvasapi.util import combine_kwargs

from auth import CanvasAPIError

from .base import MAX_PER_PAGE, _CanvasDictItem

# The only web page this module ever loads: a finished attempt's review ("history") page. Starting a quiz is a
# POST (or the /take page), so nothing here can start one: every API call is a GET, and the page URL must match this.
_REVIEW_PATH = re.compile(r"^/courses/\d+/quizzes/\d+/history$")

# New Quizzes run in their own app. A New Quiz's Canvas page hands that app a signed launch, which it trades for a
# token that can read your attempts. Opening a New Quiz never starts an attempt (that's a POST to a .../take
# endpoint, which nothing here calls), but when you have attempts left New Quizzes sets up an unstarted "pending"
# one, exactly as opening the quiz in Canvas does. These are the only requests made:
#   Canvas:      GET the assignment's launch page, then POST /api/v1/jwts for a short-lived launch token;
#   New Quizzes: POST /api/native/launch, then GETs of the paths in _NEW_QUIZ_READS only.
_LAUNCH_PATH = re.compile(r"^/courses/\d+/assignments/\d+/launch$")
_QUIZ_LTI_HOST = re.compile(r"^https://[a-z0-9-]+\.quiz-lti-[a-z0-9-]+\.instructure\.com$")
_QUIZ_API_HOST = re.compile(r"^https://[a-z0-9-]+\.quiz-api-[a-z0-9-]+\.instructure\.com$")
_NEW_QUIZ_READS = (
    re.compile(r"^/api/participant_sessions/\d+/results$"),  # your attempts, and a token to read one
    re.compile(r"^/api/quiz_sessions/\d+$"),  # one attempt: its state, times, and score
    re.compile(r"^/api/quiz_sessions/\d+/session_items$"),  # the questions as you saw them
    re.compile(r"^/api/quiz_sessions/\d+/results/\d+/session_item_results$"),  # your answers and points
)
_MAX_PAGES = 20


def _env_value(html: str, key: str) -> Any:
    """A value from the page's ENV object, or None."""
    marker = f'"{key}":'
    start = html.find(marker)
    if start < 0:
        return None
    index = start + len(marker)
    while index < len(html) and html[index].isspace():
        index += 1
    try:
        return json.JSONDecoder().raw_decode(html, index)[0]
    except ValueError:
        return None


@dataclass(frozen=True, slots=True)
class NewQuizLaunch:
    backend_url: str
    access_token: str
    participant_session_id: str
    workflow: str


class NewQuizReader:
    """GETs from New Quizzes, limited to the paths in _NEW_QUIZ_READS on New Quizzes hosts.

    Uses its own HTTP session, so Canvas cookies are never sent to New Quizzes.
    """

    def __init__(self, launch: NewQuizLaunch, http: requests.Session | None = None) -> None:
        self.launch = launch
        self.http = http or requests.Session()

    def _get(self, host: str, path: str, headers: dict[str, str], params: dict[str, str] | None = None) -> Any:
        if not (_QUIZ_LTI_HOST.fullmatch(host) or _QUIZ_API_HOST.fullmatch(host)):
            raise CanvasAPIError(f"refusing to contact {host}: not a New Quizzes host")
        if not any(pattern.fullmatch(path) for pattern in _NEW_QUIZ_READS):
            raise CanvasAPIError(f"refusing to load {path}: not a New Quizzes results read")
        try:
            response = self.http.get(
                host + path,
                headers={"Accept": "application/json", **headers},
                params=params,
                timeout=20,
                allow_redirects=False,
            )
        except requests.RequestException as exc:
            raise CanvasAPIError(f"New Quizzes request failed: {path}: {exc}") from exc
        if response.status_code != 200:
            response.close()
            raise CanvasAPIError(
                f"New Quizzes returned HTTP {response.status_code} for {path}", status_code=response.status_code
            )
        return response

    def participant_results(self, participant_session_id: str) -> dict[str, Any]:
        """Your attempts at the quiz, plus the host, token, and quiz session for this participant session."""
        return self._get(
            self.launch.backend_url,
            f"/api/participant_sessions/{participant_session_id}/results",
            {"Authorization": f"Bearer {self.launch.access_token}"},
        ).json()

    def _api(self, results: dict[str, Any], path: str, *, paginated: bool = False) -> Any:
        host, token = str(results.get("host") or ""), str(results.get("token") or "")
        headers = {"Authorization": token, "AuthType": "Signature"}
        if not paginated:
            return self._get(host, path, headers).json()
        out: list[Any] = []
        params: dict[str, str] | None = None
        for _ in range(_MAX_PAGES):
            response = self._get(host, path, headers, params)
            out.extend(response.json())
            hash_key = response.headers.get("X-Last-Evaluated-Hash-Key")
            range_key = response.headers.get("X-Last-Evaluated-Range-Key")
            if not (hash_key and range_key):
                break
            params = {"last_evaluated_hash_key": hash_key, "last_evaluated_range_key": range_key}
        return out

    def quiz_session(self, results: dict[str, Any], quiz_session_id: str) -> dict[str, Any]:
        return self._api(results, f"/api/quiz_sessions/{quiz_session_id}")

    def session_items(self, results: dict[str, Any], quiz_session_id: str) -> list[dict[str, Any]]:
        return self._api(results, f"/api/quiz_sessions/{quiz_session_id}/session_items", paginated=True)

    def item_results(self, results: dict[str, Any], quiz_session_id: str, result_id: str) -> list[dict[str, Any]]:
        return self._api(
            results,
            f"/api/quiz_sessions/{quiz_session_id}/results/{result_id}/session_item_results",
            paginated=True,
        )


class CanvasQuizzesMixin:
    """Read-only access to Classic Quizzes and the current user's own finished attempts.

    Never starts, resumes, or submits an attempt: every request is a GET, and the one web page used (a finished
    attempt's review page) is fetched without following redirects.
    """

    def list_quizzes(self, *, course_id: str, limit: int = 100) -> list[dict[str, Any]]:
        def _load(canvas: Canvas) -> list[dict[str, Any]]:
            quizzes = self._custom_paginated_call(
                canvas,
                content_class=_CanvasDictItem,
                endpoint=f"courses/{course_id}/quizzes",
                params={"per_page": MAX_PER_PAGE},
            )
            return self._take_limit(quizzes, limit=limit)

        return self._call_canvas(_load, f"list quizzes for course {course_id}")

    def get_quiz(self, *, course_id: str, quiz_id: str) -> dict[str, Any]:
        def _load(canvas: Canvas) -> dict[str, Any]:
            requester = getattr(canvas, "_Canvas__requester")
            return requester.request("GET", f"courses/{course_id}/quizzes/{quiz_id}").json()

        return self._call_canvas(_load, f"get quiz {quiz_id}")

    def list_quiz_submissions(self, *, course_id: str, quiz_id: str) -> list[dict[str, Any]]:
        """The current user's attempts at a quiz (Canvas only returns your own to a student)."""

        def _load(canvas: Canvas) -> list[dict[str, Any]]:
            requester = getattr(canvas, "_Canvas__requester")
            response = requester.request(
                "GET",
                f"courses/{course_id}/quizzes/{quiz_id}/submissions",
                _kwargs=combine_kwargs(per_page=MAX_PER_PAGE),
            )
            return list(response.json().get("quiz_submissions") or [])

        return self._call_canvas(_load, f"list attempts for quiz {quiz_id}")

    def list_submission_questions(
        self, *, course_id: str, quiz_id: str, quiz_submission_id: str, attempt: int
    ) -> list[dict[str, Any]]:
        """The questions as they were shown in one of your attempts."""

        def _load(canvas: Canvas) -> list[dict[str, Any]]:
            questions = self._custom_paginated_call(
                canvas,
                content_class=_CanvasDictItem,
                endpoint=f"courses/{course_id}/quizzes/{quiz_id}/questions",
                params={
                    "per_page": MAX_PER_PAGE,
                    "quiz_submission_id": quiz_submission_id,
                    "quiz_submission_attempt": attempt,
                },
            )
            return self._take_limit(questions, limit=300)

        return self._call_canvas(_load, f"list questions for quiz {quiz_id} attempt {attempt}")

    def get_submission_history(self, *, course_id: str, assignment_id: str) -> list[dict[str, Any]]:
        """Every version of your submission to an assignment; for a quiz, one per attempt with per-question results."""

        def _load(canvas: Canvas) -> list[dict[str, Any]]:
            requester = getattr(canvas, "_Canvas__requester")
            response = requester.request(
                "GET",
                f"courses/{course_id}/assignments/{assignment_id}/submissions/self",
                _kwargs=combine_kwargs(include=["submission_history"]),
            )
            return list(response.json().get("submission_history") or [])

        return self._call_canvas(_load, f"get submission history for assignment {assignment_id}")

    def get_quiz_review_page(
        self, *, course_id: str, quiz_id: str, quiz_submission_id: str, attempt: int
    ) -> str:
        """HTML of a finished attempt's review page, which marks the correct answers when the quiz shows them."""
        path = f"/courses/{course_id}/quizzes/{quiz_id}/history"
        if not _REVIEW_PATH.fullmatch(path):
            raise CanvasAPIError(f"refusing to load {path}: not a quiz review page")

        def _load(canvas: Canvas) -> str:
            response = self._web_get(
                canvas,
                path,
                params={"quiz_submission_id": quiz_submission_id, "version": attempt},
                allow_redirects=False,
            )
            if response.status_code != 200:
                response.close()
                raise CanvasAPIError(
                    f"quiz review page returned HTTP {response.status_code}", status_code=response.status_code
                )
            return response.text

        return self._call_canvas(_load, f"get review page for quiz {quiz_id} attempt {attempt}")

    def launch_new_quiz(self, *, course_id: str, assignment_id: str) -> NewQuizLaunch:
        """Open a New Quiz the way its Canvas page does, for a token that can read your attempts.

        Never starts an attempt (see the note at the top of this module).
        """
        path = f"/courses/{course_id}/assignments/{assignment_id}/launch"
        if not _LAUNCH_PATH.fullmatch(path):
            raise CanvasAPIError(f"refusing to load {path}: not a New Quiz launch page")

        def _load(canvas: Canvas) -> tuple[dict[str, Any], str, str]:
            response = self._web_get(canvas, path, headers={"Accept": "text/html"}, allow_redirects=False)
            if response.status_code != 200:
                response.close()
                raise CanvasAPIError(
                    f"New Quiz launch page returned HTTP {response.status_code}", status_code=response.status_code
                )
            launch = _env_value(response.text, "NEW_QUIZZES")
            account_id = _env_value(response.text, "ACCOUNT_ID")
            params = launch.get("params") if isinstance(launch, dict) else None
            if not isinstance(params, dict) or not launch.get("signature") or account_id in (None, ""):
                raise CanvasAPIError(f"assignment {assignment_id} doesn't open a New Quiz")
            launched_for = (str(params.get("custom_canvas_course_id")), str(params.get("custom_canvas_assignment_id")))
            if launched_for != (course_id, assignment_id):
                raise CanvasAPIError(f"the launch page for assignment {assignment_id} is for a different quiz")
            if not _QUIZ_LTI_HOST.fullmatch(str(params.get("backend_url") or "")):
                raise CanvasAPIError("refusing to launch: the quiz isn't hosted on New Quizzes")
            session = getattr(canvas, "_Canvas__requester")._session
            jwt = session.post(
                f"{self._root_url}/api/v1/jwts",
                params={
                    "canvas_audience": "false",
                    "workflows[]": "new_quizzes_native_launch",
                    "context_id": str(account_id),
                    "context_type": "account",
                },
                timeout=20,
                allow_redirects=False,
            )
            if jwt.status_code != 200:
                jwt.close()
                raise CanvasAPIError(
                    f"Canvas returned HTTP {jwt.status_code} for a launch token", status_code=jwt.status_code
                )
            return params, str(launch["signature"]), str(jwt.json()["token"])

        params, signature, token = self._call_canvas(_load, f"open New Quiz {assignment_id}")
        backend = str(params["backend_url"])
        try:
            response = requests.post(
                f"{backend}/api/native/launch",
                json={"params": params, "signature": signature},
                headers={
                    "Authorization": f"Bearer {token}",
                    "X-Domain": str(params.get("tool_consumer_instance_guid") or "").split(":")[0],
                },
                timeout=20,
                allow_redirects=False,
            )
        except requests.RequestException as exc:
            raise CanvasAPIError(f"New Quizzes launch failed: {exc}") from exc
        if response.status_code != 200:
            response.close()
            raise CanvasAPIError(
                f"New Quizzes launch returned HTTP {response.status_code}", status_code=response.status_code
            )
        body = response.json()
        entry = body.get("entry_path") or {}
        if not body.get("access_token") or not str(entry.get("resourceId") or "").isdigit():
            raise CanvasAPIError("New Quizzes launch didn't return a session to read")
        return NewQuizLaunch(
            backend_url=backend,
            access_token=str(body["access_token"]),
            participant_session_id=str(entry["resourceId"]),
            workflow=str(entry.get("workflow") or ""),
        )
