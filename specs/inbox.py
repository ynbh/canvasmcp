from __future__ import annotations

from specs.schema import ToolSpec, tool_spec
from tools import get_inbox_conversation, list_inbox_conversations
from tools.inbox import INBOX_SCOPES

INBOX_TOOL_SPECS: list[ToolSpec] = [
    tool_spec(
        name="list_inbox_conversations",
        read_only=True,
        description=(
            "List the current user's Canvas Inbox conversations (messages from "
            "instructors and classmates), newest first. Does not mark anything as read."
        ),
        handler=list_inbox_conversations,
        properties={
            "scope": {
                "type": "string",
                "enum": list(INBOX_SCOPES),
                "description": "Which view to list. Defaults to inbox.",
            },
            "course_id": {"type": "string", "description": "Only conversations for this course."},
            "limit": {"type": "integer", "minimum": 1, "maximum": 300},
        },
    ),
    tool_spec(
        name="get_inbox_conversation",
        read_only=True,
        description=(
            "Get every message in one Canvas Inbox conversation, newest first. "
            "Leaves the conversation's read or unread state unchanged."
        ),
        handler=get_inbox_conversation,
        properties={"conversation_id": {"type": "string"}},
        required=["conversation_id"],
    ),
]
