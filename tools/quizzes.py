from __future__ import annotations

import json
from datetime import datetime, timezone
from html.parser import HTMLParser
from typing import Any

from auth import CanvasAPIError
from client.quizzes import NewQuizReader
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
            "New Quizzes show dates, points, and your score here. For a New Quiz's questions and your answers, "
            "use get_new_quiz_results with its assignment_id."
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


# -- New Quizzes ---------------------------------------------------------------------------------------
# Canvas's submission states that mean at least one attempt was handed in. Nothing is opened before Canvas says so.
CANVAS_SUBMITTED = ("submitted", "graded", "pending_review")
# New Quizzes' states for a finished attempt; anything else (pending, started, in progress) is never read.
NEW_QUIZ_FINISHED = ("submitted", "graded", "needs_review", "pending_review", "complete", "completed")
NEW_QUIZ_NOTE = (
    "Read-only: this opens the quiz the same way its Canvas page does, which never starts an attempt, and only "
    "finished attempts are read."
)
SINGLE_CHOICE = ("choice", "true-false")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(value: Any) -> datetime | None:
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")) if value else None
    except ValueError:
        return None


def _in_window(show_at: Any, hide_at: Any) -> bool:
    show, hide, now = _iso(show_at), _iso(hide_at), _now()
    return (show is None or show <= now) and (hide is None or now < hide)


def _visibility(participant_session: dict[str, Any]) -> dict[str, bool]:
    """What New Quizzes lets you see of one attempt.

    Whether the questions show at all is New Quizzes' own decision (can_see_results_items). Within them, a setting
    the instructor turned off stays off; a setting that isn't listed is only shown when results aren't restricted.
    """
    vp = participant_session.get("view_permissions") or {}
    restricted = bool(vp.get("result_view_restricted"))
    last_done = not vp.get("attempts_remain")

    def allowed(flag: str) -> bool:
        return bool(vp[flag]) if flag in vp else not restricted

    def qualified(qualifier: str) -> bool:
        return "after_last_attempt" not in str(vp.get(qualifier) or "always") or last_done

    items = (
        bool(participant_session.get("can_see_results_page"))
        and bool(participant_session.get("can_see_results_items"))
        and allowed("display_items")
    )
    responses = (
        items
        and allowed("display_item_response")
        and qualified("display_item_response_qualifier")
        and _in_window(vp.get("show_item_responses_at"), vp.get("hide_item_responses_at"))
    )
    correctness = (
        responses
        and allowed("display_item_response_correctness")
        and qualified("display_item_response_correctness_qualifier")
        and _in_window(vp.get("show_item_response_correctness_at"), vp.get("hide_item_response_correctness_at"))
    )
    return {
        "questions": items,
        "your_answers": responses,
        "points": allowed("display_points_awarded"),
        "correctness": correctness,
        "correct_answers": correctness and allowed("display_item_correct_answer"),
        "feedback": responses and allowed("display_item_feedback"),
    }


def _nq_choices(slug: str, data: dict[str, Any]) -> dict[str, Any] | None:
    if slug == "true-false":
        return {"true": data.get("true_choice") or "True", "false": data.get("false_choice") or "False"}
    choices = data.get("choices")
    if isinstance(choices, list):
        ordered = sorted((c for c in choices if isinstance(c, dict)), key=lambda c: c.get("position") or 0)
        return {str(c.get("id")): truncate_html(c.get("item_body"), limit=500) for c in ordered}
    return None


def _raw(value: Any) -> Any:
    if value in (None, "", [], {}):
        return None
    if isinstance(value, str):
        return truncate_html(value, limit=QUESTION_CHAR_LIMIT)
    if isinstance(value, (int, float, bool)):
        return value
    return json.dumps(value)[:QUESTION_CHAR_LIMIT]


def _feedback(result: dict[str, Any], picked: list[str]) -> list[str] | None:
    out = []
    item_feedback = (result.get("feedback") or {}).get("item_feedback") or {}
    if isinstance(item_feedback, dict):
        out += [truncate_html(v, limit=1000) for v in item_feedback.values() if isinstance(v, str) and v.strip()]
    answer_feedback = result.get("answer_feedback") or {}
    if isinstance(answer_feedback, dict):
        out += [truncate_html(answer_feedback[k], limit=1000) for k in picked if isinstance(answer_feedback.get(k), str)]
    return [text for text in out if text] or None


def _nq_question(session_item: dict[str, Any], result: dict[str, Any], show: dict[str, bool]) -> dict[str, Any]:
    item = session_item.get("item") or {}
    slug = str((item.get("interaction_type") or {}).get("slug") or "")
    choices = _nq_choices(slug, item.get("interaction_data") or {})
    scored = result.get("scored_data") or {}
    value = scored.get("value")
    yours: Any = None
    correct_answers: Any = None
    picked: list[str] = []
    if choices is not None and isinstance(value, dict) and all(isinstance(v, dict) for v in value.values()):
        picked = [k for k, v in value.items() if v.get("user_responded")]
        right = [k for k, v in value.items() if (v.get("result_score") or 0) > 0]
        yours = [choices.get(k, k) for k in picked]
        correct_answers = [choices.get(k, k) for k in right] or None
        if slug in SINGLE_CHOICE:
            yours = yours[0] if yours else None
    else:
        yours = _raw(value)
    stimulus = session_item.get("stimulus")
    question = {
        "position": session_item.get("position"),
        "type": slug or None,
        "question": truncate_html(item.get("item_body"), limit=QUESTION_CHAR_LIMIT),
        "passage": truncate_html(stimulus.get("body"), limit=QUESTION_CHAR_LIMIT)
        if isinstance(stimulus, dict) and stimulus.get("body")
        else None,
        "choices": list(choices.values()) if choices and slug != "true-false" else None,
        "points_possible": result.get("points_possible", session_item.get("points_possible")),
    }
    if show["your_answers"]:
        question["your_answer"] = yours
    if show["points"]:
        question["points"] = result.get("score")
    if show["correctness"]:
        question["result"] = scored.get("correct")
    if show["correct_answers"]:
        question["correct_answers"] = correct_answers
    if show["feedback"]:
        question["feedback"] = _feedback(result, picked)
    if scored.get("grade_status"):
        question["grade_status"] = scored.get("grade_status")
    return question


def get_new_quiz_results(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    assignment_id = str(args.get("assignment_id", "")).strip()
    if error := _bad_id(course_id=course_id, assignment_id=assignment_id):
        return error
    wanted = args.get("attempt")
    client = canvas_client()
    assignment = client.get_assignment(
        course_id=course_id, assignment_id=assignment_id, include_submission=True, include_discussion_topic=False
    )
    if not assignment.get("is_quiz_lti_assignment"):
        if assignment.get("quiz_id"):
            return invalid_argument(
                f"assignment {assignment_id} is a Classic Quiz; use get_quiz_results with quiz_id "
                f"{assignment['quiz_id']}"
            )
        return invalid_argument(f"assignment {assignment_id} isn't a New Quiz")
    result: dict[str, Any] = {
        "course_id": course_id,
        "assignment_id": assignment_id,
        "title": assignment.get("name"),
        "points_possible": assignment.get("points_possible"),
        "due_at": assignment.get("due_at"),
        "note": NEW_QUIZ_NOTE,
    }
    submission = assignment.get("submission") or {}
    if not (int(submission.get("attempt") or 0) >= 1 and submission.get("workflow_state") in CANVAS_SUBMITTED):
        # Nothing has been handed in, so the quiz isn't opened at all.
        result["message"] = "No finished attempt to show yet."
        return result

    reader = NewQuizReader(client.launch_new_quiz(course_id=course_id, assignment_id=assignment_id))
    entry = reader.participant_results(reader.launch.participant_session_id)
    history = [h for h in entry.get("attempt_history") or [] if str(h.get("id") or "").isdigit()]
    attempts = [
        {
            "attempt": number,
            "percentage": round(float(h["percentage"]) * 100, 1) if h.get("percentage") is not None else None,
            "kept": h.get("authoritative"),
        }
        for number, h in enumerate(history, start=1)
    ]
    # New Quizzes can leave a finished attempt out of the history (its record still says in progress even though
    # the attempt inside was submitted). Then the current record is the only candidate, and it's only read below
    # if its attempt really is finished.
    sessions = [str(h["id"]) for h in history] or [str(reader.launch.participant_session_id)]
    if wanted is not None and int(wanted) > len(sessions):
        return invalid_argument(f"attempt {int(wanted)} isn't a finished attempt")
    index = int(wanted) - 1 if wanted is not None else len(sessions) - 1
    chosen = entry if sessions[index] == str(reader.launch.participant_session_id) else None
    chosen = chosen or reader.participant_results(sessions[index])
    quiz_session_id = str(chosen.get("quiz_api_quiz_session_id") or "")
    if not quiz_session_id.isdigit():
        result["message"] = "New Quizzes didn't say which attempt to read."
        return result
    session = reader.quiz_session(chosen, quiz_session_id)
    quiz = session.get("quiz") or {}
    scored = session.get("authoritative_result") or {}
    number = index + 1 if history else session.get("attempt")
    if not history and number is not None:
        attempts = [{"attempt": number, "percentage": None, "kept": True}]
    result.update(
        {
            "title": quiz.get("title") or result["title"],
            "instructions": truncate_html(quiz.get("instructions"), limit=QUESTION_CHAR_LIMIT) or None,
            "allowed_attempts": entry.get("max_attempts") or None,
            "attempts": attempts,
            "attempt": number,
        }
    )
    if session.get("status") not in NEW_QUIZ_FINISHED or not session.get("submitted_at"):
        result["message"] = "This attempt isn't finished, so nothing in it is read."
        return result
    if attempts and attempts[-1]["percentage"] is None and scored.get("percentage") is not None:
        attempts[-1]["percentage"] = round(float(scored["percentage"]) * 100, 1)
    show = _visibility(chosen.get("participant_session") or {})
    result.update(
        {
            "score": scored.get("score") if show["points"] else None,
            "attempt_points_possible": scored.get("points_possible"),
            "started_at": session.get("start_at"),
            "submitted_at": session.get("submitted_at"),
            "shown": show,
        }
    )
    if not show["questions"]:
        result["message"] = "New Quizzes doesn't show you this attempt's questions, so only the score is shown."
        return result
    items = reader.session_items(chosen, quiz_session_id)
    item_results: list[dict[str, Any]] = []
    if scored.get("id") is not None and str(scored["id"]).isdigit():
        item_results = reader.item_results(chosen, quiz_session_id, str(scored["id"]))
    by_item = {str(r.get("item_id")): r for r in item_results}
    questions = [
        _nq_question(si, by_item.get(str((si.get("item") or {}).get("id")), {}), show)
        for si in sorted(items, key=lambda si: si.get("position") or 0)
    ]
    result.update({"question_count": len(questions), "questions": questions})
    hidden = [name.replace("_", " ") for name, on in show.items() if not on]
    if hidden:
        result["hidden_by_quiz_settings"] = hidden
    return result
