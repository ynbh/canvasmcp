from __future__ import annotations

from specs.schema import ToolSpec, tool_spec
from tools.planner import (
    PLANNABLE_TYPES,
    create_todo_note,
    delete_todo_note,
    list_planner_items,
    set_todo_item_state,
    update_todo_note,
)

PLANNER_TOOL_SPECS: list[ToolSpec] = [
    tool_spec(
        name="list_planner_items",
        read_only=True,
        description=(
            "List your Canvas To Do list (planner) between two dates: assignments, quizzes, discussions, events, "
            "and your own to-do notes, each with whether you've marked it done or dismissed it, and whether it's "
            "submitted. Use plannable_type and plannable_id with set_todo_item_state, and note_id for notes."
        ),
        handler=list_planner_items,
        properties={
            "start_date": {"type": "string", "description": "YYYY-MM-DD; defaults to today."},
            "end_date": {"type": "string", "description": "YYYY-MM-DD."},
            "incomplete_only": {"type": "boolean", "description": "Only items not done yet."},
            "limit": {"type": "integer", "minimum": 1, "maximum": 300},
        },
    ),
    tool_spec(
        name="create_todo_note",
        description="Add a personal to-do item to your Canvas To Do list. Only you can see it.",
        handler=create_todo_note,
        properties={
            "title": {"type": "string"},
            "details": {"type": "string"},
            "todo_date": {"type": "string", "description": "YYYY-MM-DD or an ISO date-time."},
            "course_id": {"type": "string", "description": "Optional course to file it under."},
        },
        required=["title"],
    ),
    tool_spec(
        name="update_todo_note",
        description="Change one of your personal to-do items: its title, details, date, or course.",
        handler=update_todo_note,
        properties={
            "note_id": {"type": "string"},
            "title": {"type": "string"},
            "details": {"type": "string"},
            "todo_date": {"type": "string", "description": "YYYY-MM-DD or an ISO date-time."},
            "course_id": {"type": "string"},
        },
        required=["note_id"],
    ),
    tool_spec(
        name="delete_todo_note",
        description="Delete one of your personal to-do items. Can't be undone.",
        handler=delete_todo_note,
        properties={"note_id": {"type": "string"}},
        required=["note_id"],
    ),
    tool_spec(
        name="set_todo_item_state",
        description=(
            "Mark a To Do item done or not done, or dismiss it from the list, like the checkbox in Canvas. "
            "Only changes your To Do list; it never submits anything."
        ),
        handler=set_todo_item_state,
        properties={
            "plannable_type": {"type": "string", "enum": list(PLANNABLE_TYPES)},
            "plannable_id": {"type": "string"},
            "done": {"type": "boolean"},
            "dismissed": {"type": "boolean"},
        },
        required=["plannable_type", "plannable_id"],
    ),
]
