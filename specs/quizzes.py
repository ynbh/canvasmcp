from __future__ import annotations

from specs.schema import ToolSpec, tool_spec
from tools.quizzes import get_new_quiz_results, get_quiz_results, list_course_quizzes

QUIZ_TOOL_SPECS: list[ToolSpec] = [
    tool_spec(
        name="list_course_quizzes",
        read_only=True,
        description=(
            "List a course's quizzes with their settings and your status: type, points, question count, time "
            "limit, attempts allowed and left, unlock, due, and lock dates, lockdown or access-code requirements, "
            "your score, and the quiz instructions. Includes New Quizzes (dates, points, and score only; read "
            "their results with get_new_quiz_results). Never opens or starts a quiz."
        ),
        handler=list_course_quizzes,
        properties={
            "course_id": {"type": "string"},
            "limit": {"type": "integer", "minimum": 1, "maximum": 300},
        },
        required=["course_id"],
    ),
    tool_spec(
        name="get_quiz_results",
        read_only=True,
        description=(
            "Your finished attempts at a Classic Quiz: each attempt's score and time, and for one attempt (the "
            "latest by default) every question with its choices, your answer, whether it was right, the points, "
            "and the correct answer when the quiz shows it. Only reads finished attempts; never opens, starts, or "
            "resumes one, and reads nothing while an attempt is in progress."
        ),
        handler=get_quiz_results,
        properties={
            "course_id": {"type": "string"},
            "quiz_id": {"type": "string"},
            "attempt": {
                "type": "integer",
                "minimum": 1,
                "description": "Attempt number; defaults to the latest.",
            },
        },
        required=["course_id", "quiz_id"],
    ),
    tool_spec(
        name="get_new_quiz_results",
        read_only=True,
        description=(
            "Your finished attempts at a New Quiz (by its assignment_id from list_course_quizzes): each attempt's "
            "score, and for one attempt (the latest by default) every question with its choices, your answer, the "
            "points, whether it was right, the correct answer, and feedback, as far as the quiz's result settings "
            "show them. Opens the quiz only after Canvas shows a submitted attempt, the same way its Canvas page "
            "does, which never starts an attempt; only finished attempts are read."
        ),
        handler=get_new_quiz_results,
        properties={
            "course_id": {"type": "string"},
            "assignment_id": {"type": "string"},
            "attempt": {
                "type": "integer",
                "minimum": 1,
                "description": "Attempt number; defaults to the latest.",
            },
        },
        required=["course_id", "assignment_id"],
    ),
]
