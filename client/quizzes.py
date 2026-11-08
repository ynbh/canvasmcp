from __future__ import annotations

import re
from typing import Any

from canvasapi import Canvas
from canvasapi.util import combine_kwargs

from auth import CanvasAPIError

from .base import MAX_PER_PAGE, _CanvasDictItem

# The only web page this module ever loads: a finished attempt's review ("history") page. Starting a quiz is a
# POST (or the /take page), so nothing here can start one: every API call is a GET, and the page URL must match this.
_REVIEW_PATH = re.compile(r"^/courses/\d+/quizzes/\d+/history$")


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
