from __future__ import annotations

from html.parser import HTMLParser
from typing import Any

from auth import CanvasAPIError
from tools.common import canvas_client, invalid_argument, looks_like_canvas_id, truncate_html

# Reading quizzes is safe; taking one is not. Nothing here starts, resumes, or submits an attempt (see
# client/quizzes.py): the list only reads quiz settings and assignment records, and results are only read for
# attempts that are already finished.
FINISHED = ("complete", "pending_review")
QUESTION_CHAR_LIMIT = 4000
CHOICE_TYPES = ("multiple_choice_question", "true_false_question", "multiple_answers_question")
QUIZ_TYPES = {
    "assignment": "graded quiz",
    "practice_quiz": "practice quiz",
    "graded_survey": "graded survey",
    "survey": "survey",
}
SAFETY_NOTE = "Read-only: nothing here opens or starts a quiz attempt."
# Canvas answers 404 for a Quizzes page hidden from students; some setups answer 401 or 403 instead.
HIDDEN_STATUSES = (401, 403, 404)


def _bad_id(**ids: str) -> dict[str, Any] | None:
    # IDs go into request paths, so anything but a Canvas ID is refused before a request is made.
    for name, value in ids.items():
        if not looks_like_canvas_id(value):
            return invalid_argument(f"{name} must be a Canvas ID")
    return None


def _attempts_left(allowed: Any, used: int) -> int | str | None:
    if allowed is None:
        return None
    if int(allowed) < 0:
        return "unlimited"
    return max(int(allowed) - used, 0)


def _my_status(submission: dict[str, Any] | None, allowed: Any) -> dict[str, Any]:
    s = submission or {}
    used = int(s.get("attempt") or 0)
    return {
        "state": s.get("workflow_state") or "unsubmitted",
        "score": s.get("score"),
        "submitted_at": s.get("submitted_at"),
        "attempts_used": used,
        "attempts_left": _attempts_left(allowed, used),
        "late": s.get("late"),
        "missing": s.get("missing"),
    }


def _classic_summary(quiz: dict[str, Any], submission: dict[str, Any] | None) -> dict[str, Any]:
    allowed = quiz.get("allowed_attempts")
    return {
        "kind": "classic_quiz",
        "quiz_id": str(quiz.get("id", "")),
        "assignment_id": str(quiz["assignment_id"]) if quiz.get("assignment_id") else None,
        "title": quiz.get("title"),
        "type": QUIZ_TYPES.get(quiz.get("quiz_type"), quiz.get("quiz_type")),
        "instructions": truncate_html(quiz.get("description"), limit=1000) or None,
        "points_possible": quiz.get("points_possible"),
        "question_count": quiz.get("question_count"),
        "time_limit_minutes": quiz.get("time_limit"),
        "allowed_attempts": "unlimited" if allowed is not None and int(allowed) < 0 else allowed,
        "scoring_policy": quiz.get("scoring_policy"),
        "unlock_at": quiz.get("unlock_at"),
        "due_at": quiz.get("due_at"),
        "lock_at": quiz.get("lock_at"),
        "published": quiz.get("published"),
        "locked_for_you": quiz.get("locked_for_user"),
        "lock_explanation": truncate_html(quiz.get("lock_explanation"), limit=300),
        "one_question_at_a_time": quiz.get("one_question_at_a_time"),
        "cant_go_back": quiz.get("cant_go_back"),
        "shuffle_answers": quiz.get("shuffle_answers"),
        "requires_access_code": quiz.get("has_access_code"),
        "requires_lockdown_browser": quiz.get("require_lockdown_browser"),
        "shows_correct_answers": quiz.get("show_correct_answers"),
        "show_correct_answers_at": quiz.get("show_correct_answers_at"),
        "hide_correct_answers_at": quiz.get("hide_correct_answers_at"),
        "hides_results": quiz.get("hide_results"),
        # Practice quizzes and surveys aren't assignments, so their attempts only show up in get_quiz_results.
        "your_status": _my_status(submission, allowed) if quiz.get("assignment_id") else None,
    }


def _new_quiz_summary(assignment: dict[str, Any]) -> dict[str, Any]:
    # A New Quiz keeps its time limit and attempt limit inside the quiz app; the assignment's allowed_attempts
    # usually says unlimited regardless, so neither is reported.
    return {
        "kind": "new_quiz",
        "assignment_id": str(assignment.get("id", "")),
        "title": assignment.get("name"),
        "points_possible": assignment.get("points_possible"),
        "unlock_at": assignment.get("unlock_at"),
        "due_at": assignment.get("due_at"),
        "lock_at": assignment.get("lock_at"),
        "locked_for_you": assignment.get("locked_for_user"),
        "your_status": _my_status(assignment.get("submission"), None),
    }


def list_course_quizzes(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    if error := _bad_id(course_id=course_id):
        return error
    limit = int(args.get("limit", 100))
    client = canvas_client()
    notes = [SAFETY_NOTE]
    hidden = False
    try:
        quizzes = client.list_quizzes(course_id=course_id, limit=limit)
    except CanvasAPIError as exc:
        if exc.status_code not in HIDDEN_STATUSES:
            raise
        quizzes, hidden = [], True
    assignments = client.list_assignments(
        course_id=course_id, include_submission=True, include_discussion_topic=False, limit=300
    )
    by_id = {str(a.get("id")): a for a in assignments}
    if hidden:
        # Each Classic Quiz is also an assignment (submission type online_quiz) that names its quiz_id, and the
        # quiz itself can still be read even though its list page is hidden.
        quiz_ids = [
            str(a["quiz_id"])
            for a in assignments
            if a.get("quiz_id") and "online_quiz" in (a.get("submission_types") or [])
        ][:limit]
        unreadable = []
        for quiz_id in quiz_ids:
            try:
                quizzes.append(client.get_quiz(course_id=course_id, quiz_id=quiz_id))
            except CanvasAPIError as exc:  # one restricted or unpublished quiz shouldn't hide the rest
                if exc.status_code not in HIDDEN_STATUSES:
                    raise
                unreadable.append(quiz_id)
        notes.append(
            "This course hides its Quizzes page from students, so its Classic Quizzes were found through "
            "their assignments."
        )
        if unreadable:
            notes.append(f"Canvas wouldn't show {len(unreadable)} of them (quiz IDs {', '.join(unreadable)}).")
    items = [
        _classic_summary(q, (by_id.get(str(q.get("assignment_id"))) or {}).get("submission"))
        for q in quizzes
    ]
    new = [_new_quiz_summary(a) for a in assignments if a.get("is_quiz_lti_assignment")]
    if new:
        notes.append(
            "New Quizzes show dates, points, and your score. Their time and attempt limits, questions, "
            "and answers live inside the New Quizzes app, which students can't read through the API."
        )
    items += new[: max(limit - len(items), 0)]
    return {"course_id": course_id, "count": len(items), "quizzes": items, "notes": notes}


class _ReviewPage(HTMLParser):
    """Per question on a review page: each answer's ID, text, and whether it's marked correct or chosen."""

    VOID = ("br", "img", "input", "hr", "meta", "link")

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.questions: dict[str, list[dict[str, Any]]] = {}
        self._question: str | None = None
        self._answer: dict[str, Any] | None = None
        self._depth = 0
        self._answer_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self.VOID:
            return
        self._depth += 1
        attributes = dict(attrs)
        classes = (attributes.get("class") or "").split()
        element_id = attributes.get("id") or ""
        if "question" in classes and element_id.startswith("question_") and element_id[9:].isdigit():
            self._question = element_id[9:]
            self.questions.setdefault(self._question, [])
        elif self._question and self._answer is None and "answer" in classes and element_id.startswith("answer_"):
            self._answer = {
                "id": element_id[7:],
                "correct": "correct_answer" in classes,
                "selected": "selected_answer" in classes,
                "text": [],
            }
            self._answer_depth = self._depth
            self.questions[self._question].append(self._answer)

    def handle_endtag(self, tag: str) -> None:
        if tag in self.VOID:
            return
        if self._answer is not None and self._depth == self._answer_depth:
            self._answer["text"] = " ".join(" ".join(self._answer["text"]).split())
            self._answer = None
        self._depth -= 1

    def handle_data(self, data: str) -> None:
        if self._answer is not None and data.strip():
            self._answer["text"].append(data.strip())


def _review_marks(html: str) -> dict[str, list[dict[str, Any]]]:
    page = _ReviewPage()
    page.feed(html)
    return page.questions


def _choice_text(answer: dict[str, Any]) -> Any:
    return answer.get("text") or truncate_html(answer.get("html"), limit=500)


def _your_answer(question: dict[str, Any], data: dict[str, Any]) -> Any:
    """Your answer in readable form, from the attempt's per-question record."""
    qtype = question.get("question_type")
    choices = {str(a.get("id")): _choice_text(a) for a in question.get("answers") or []}
    if qtype in ("multiple_choice_question", "true_false_question"):
        answer_id = data.get("answer_id")
        return choices.get(str(answer_id), answer_id) if answer_id is not None else None
    if qtype == "multiple_answers_question":
        return [choices.get(k[7:], k[7:]) for k, v in data.items() if k.startswith("answer_") and str(v) == "1"]
    if qtype == "matching_question":
        matches = {str(m.get("match_id")): m.get("text") for m in question.get("matches") or []}
        return {
            choices.get(k[7:], k[7:]): matches.get(str(v), v)
            for k, v in data.items()
            if k.startswith("answer_") and k[7:].isdigit() and v not in (None, "")
        }
    if qtype in ("fill_in_multiple_blanks_question", "multiple_dropdowns_question"):
        out = {}
        for k, v in data.items():
            if k.startswith("answer_for_"):
                blank = k[len("answer_for_") :]
                picked = data.get(f"answer_id_for_{blank}")
                out[blank] = choices.get(str(picked), v) if qtype == "multiple_dropdowns_question" and picked else v
        return out
    if qtype == "file_upload_question":
        return {"attachment_ids": data.get("attachment_ids")}
    text = data.get("text")
    return truncate_html(text, limit=QUESTION_CHAR_LIMIT) if text not in (None, "") else None


def _correct_answers(
    question: dict[str, Any], data: dict[str, Any], marks: list[dict[str, Any]] | None, yours: Any
) -> tuple[Any, str | None]:
    qtype = question.get("question_type")
    if marks and qtype in CHOICE_TYPES + ("fill_in_multiple_blanks_question",):
        choices = {str(a.get("id")): a.get("text") for a in question.get("answers") or []}
        marked = [choices.get(m["id"]) or m["text"] for m in marks if m["correct"]]
        if marked:
            return marked, "review_page"
    if data.get("correct") is True and yours not in (None, "", [], {}):
        return yours, "your_correct_answer"
    return None, None


def get_quiz_results(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    quiz_id = str(args.get("quiz_id", "")).strip()
    if error := _bad_id(course_id=course_id, quiz_id=quiz_id):
        return error
    wanted = args.get("attempt")
    client = canvas_client()
    quiz = client.get_quiz(course_id=course_id, quiz_id=quiz_id)
    submissions = client.list_quiz_submissions(course_id=course_id, quiz_id=quiz_id)
    history: list[dict[str, Any]] = []
    if quiz.get("assignment_id"):
        history = client.get_submission_history(course_id=course_id, assignment_id=str(quiz["assignment_id"]))
    result: dict[str, Any] = {
        "course_id": course_id,
        "quiz_id": quiz_id,
        "title": quiz.get("title"),
        "type": QUIZ_TYPES.get(quiz.get("quiz_type"), quiz.get("quiz_type")),
        "points_possible": quiz.get("points_possible"),
        "time_limit_minutes": quiz.get("time_limit"),
        "allowed_attempts": quiz.get("allowed_attempts"),
        "scoring_policy": quiz.get("scoring_policy"),
        "instructions": truncate_html(quiz.get("description"), limit=QUESTION_CHAR_LIMIT) or None,
        "note": SAFETY_NOTE,
    }

    in_progress = [s for s in submissions if s.get("workflow_state") == "untaken"]
    finished = [s for s in submissions if s.get("workflow_state") in FINISHED]
    by_attempt = {int(v.get("attempt") or 0): v for v in history if v.get("attempt")}
    attempts = [
        {
            "attempt": number,
            "score": version.get("score"),
            "submitted_at": version.get("submitted_at"),
            "state": version.get("workflow_state"),
        }
        for number, version in sorted(by_attempt.items())
    ]
    for s in finished:  # timing comes from the quiz submission, which describes its latest attempt
        row = next((a for a in attempts if a["attempt"] == s.get("attempt")), None)
        if row is None:
            row = {"attempt": s.get("attempt"), "score": s.get("score")}
            attempts.append(row)
        row.update(
            {
                "started_at": s.get("started_at"),
                "finished_at": s.get("finished_at"),
                "minutes_spent": round((s.get("time_spent") or 0) / 60, 1),
                "kept_score": s.get("kept_score"),
            }
        )
    result["attempts"] = sorted(attempts, key=lambda a: a["attempt"] or 0)
    if in_progress:
        result["in_progress"] = "You have an attempt in progress. It isn't read here, and its timer is Canvas's."
    if not finished:
        result["message"] = (
            "An attempt is in progress, so nothing is read until it's finished."
            if in_progress
            else "No finished attempt to show yet."
        )
        return result
    if quiz.get("hide_results") == "always":
        result["message"] = "This quiz hides results from students, so only scores are shown."
        return result

    latest = max(finished, key=lambda s: int(s.get("attempt") or 0))
    number = int(wanted) if wanted is not None else int(latest.get("attempt") or 1)
    if number > int(latest.get("attempt") or 0) or (in_progress and number == in_progress[0].get("attempt")):
        return invalid_argument(f"attempt {number} isn't a finished attempt")
    submission_id = str(latest["id"])  # one quiz submission holds every attempt; versions are picked by number

    questions = client.list_submission_questions(
        course_id=course_id, quiz_id=quiz_id, quiz_submission_id=submission_id, attempt=number
    )
    data = {str(d.get("question_id")): d for d in (by_attempt.get(number) or {}).get("submission_data") or []}
    marks: dict[str, list[dict[str, Any]]] = {}
    if quiz.get("show_correct_answers"):
        try:
            marks = _review_marks(
                client.get_quiz_review_page(
                    course_id=course_id, quiz_id=quiz_id, quiz_submission_id=submission_id, attempt=number
                )
            )
        except CanvasAPIError as exc:
            result["review_page"] = f"Couldn't read the review page ({exc}); correct answers are limited."
    else:
        result["review_page"] = "This quiz doesn't show correct answers, so only your own results are shown."

    items = []
    for q in sorted(questions, key=lambda q: q.get("position") or 0):
        qid = str(q.get("id"))
        d = data.get(qid, {})
        yours = _your_answer(q, d)
        correct, source = _correct_answers(q, d, marks.get(qid), yours)
        items.append(
            {
                "position": q.get("position"),
                "question_id": qid,
                "name": q.get("question_name"),
                "type": q.get("question_type"),
                "question": truncate_html(q.get("question_text"), limit=QUESTION_CHAR_LIMIT),
                "choices": [_choice_text(a) for a in q.get("answers") or []] or None,
                "matches": [m.get("text") for m in q.get("matches") or []] or None,
                "your_answer": yours,
                "result": d.get("correct"),
                "points": d.get("points"),
                "correct_answers": correct,
                "correct_answers_source": source,
            }
        )
    result.update(
        {
            "attempt": number,
            "score": (by_attempt.get(number) or {}).get("score", latest.get("score")),
            "question_count": len(items),
            "questions": items,
        }
    )
    return result
