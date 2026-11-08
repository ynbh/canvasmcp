from __future__ import annotations

from specs.schema import ToolSpec, tool_spec
from tools.quizzes import get_quiz_results, list_course_quizzes

QUIZ_TOOL_SPECS: list[ToolSpec] = [
    tool_spec(
        name="list_course_quizzes",
        read_only=True,
        description=(
            "List a course's quizzes with their settings and your status: type, points, question count, time "
            "limit, attempts allowed and left, unlock, due, and lock dates, lockdown or access-code requirements, "
            "your score, and the quiz instructions. Includes New Quizzes (dates, points, and score only). "
            "Never opens or starts a quiz."
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
]
